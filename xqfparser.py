#-*- coding: UTF-8 -*-
'''
 作者：云中买马
 公众号：编程想法
 博客：https://blog.yuccn.net
 邮箱：yuccnx@gmail.com
 代码功能：XQF 棋谱 读写解析器
'''

import os
from collections import namedtuple

from data import *
from fen_tool import *

# 常量
# 密钥流掩码
# 来自：https://github.com/xqbase/eleeye/blob/master/XQFTOOLS/xqf2pgn.cpp
encStreamMask = "[(C) Copyright Mr. Dong Shiwei.]"


'''
  01 - 16: 依次为红方的车马相士帅士相马车炮炮兵兵兵兵兵
  17 - 32: 依次为黑方的车马象士将士象马车炮炮卒卒卒卒卒
  说明来自：https://github.com/xqbase/eleeye/blob/master/XQFTOOLS/XQF.TXT
'''
cpcXqf2Piece = [
  13, 12, 11, 10, 9, 10, 11, 12, 13, 14, 14, 15, 15, 15, 15, 15,
  21, 20, 19, 18, 17, 18, 19, 20, 21, 22, 22, 23, 23, 23, 23, 23
]

# XQF 版本11 之后会加密，所以带有加密字段偏移
Encryption = namedtuple("Encryption", [
    'encStream',
    'pieceOff',  # 局面初始位置的加密偏移值
    'srcOff',    # 着法起点的加密偏移值
    'dstOff',    # 着法终点的加密偏移值
    'commentOff' # 注释的加密偏移值
    ])

class XQFParser():
    def __init__(self):
        pass

# XQF棋谱读取器
class XQFReader(XQFParser):
    def __init__(self):
        pass

    def _square54Plus221(self, x):
        return x * x * 54 + 221

    # 读取字符串块，“第一个byte 是程度，后面是字符串内容” 的数据
    # [len][str……]
    def _readStrBlock(self, datas, pos, assertMaxLen):
        length = datas[pos]
        assert(length <= assertMaxLen)
        pos += 1

        return datas[pos:pos+length].decode("gbk")


    def read(self, file_path, qipu):
        fsize = os.path.getsize(file_path)
        assert(fsize < 1024 * 500) # 不应该大于500 k

        file = open(file_path, 'rb')
        datas = file.read(fsize)
        file.close()

        # 读取标记
        self._readFlag(datas)

        # 结果
        result = self._readResult(datas)
        results = [RESULT_UNKNOWN, RESULT_WIN_RED, RESULT_WIN_BLACK, RESULT_PEACE]
        qipu.result = results[result]

        # 类型
        _type = self._readType(datas)
        addr = [TYPE_FULL, TYPE_START, TYPE_MIDDLE, TYPE_END]
        qipu.type = addr[_type]

        # 读取标题
        qipu.title = self._readStrBlock(datas, 0x50, 63)
        qipu.gameName = self._readStrBlock(datas, 0xD0, 63)
        qipu.gameDate = self._readStrBlock(datas, 0x110, 15)
        qipu.gamePlace = self._readStrBlock(datas, 0x120, 15)
        qipu.redName = self._readStrBlock(datas, 0x130, 15)
        qipu.blackName = self._readStrBlock(datas, 0x140, 15)
        qipu.timeRule = self._readStrBlock(datas, 0x150, 63)
        qipu.redTime = self._readStrBlock(datas, 0x190, 15)
        qipu.blackTime = self._readStrBlock(datas, 0x1A0, 15)
        qipu.commenter = self._readStrBlock(datas, 0x1D0, 15)
        qipu.author = self._readStrBlock(datas, 0x1E0, 15)

        # 便可读取加密信息
        encrypt = self._readEncryption(datas)

        # 初始局面信息
        qipu.squares = self._readSquares(datas, encrypt)

        # 读取棋谱
        self._buildMoves(datas, encrypt, qipu)

    def _readFlag(self, datas):
        # 标记 在0开始
        flag = datas[:2].decode('gbk')  # 读取2个字节
        assert(flag == "XQ")

        return flag

    def _readVersion(self, datas):
        version = datas[2]

        return version

    def _readEncryption(self, datas):
        # 参考 https://github.com/xqbase/eleeye/blob/master/XQFTOOLS/xqf2pgn.cpp#L60
        if self._readVersion(datas) < 11:
            return Encryption([0 for i in range(32)], 0, 0, 0, 0)

        tags = datas[0:16]

        # 局面初始位置的加密偏移值
        pieceOff = 0xFF & (self._square54Plus221(tags[13]) * tags[13])
        # 着法起点的加密偏移值
        srcOff = 0xFF & (self._square54Plus221(tags[14]) * pieceOff)
        # 着法终点的加密偏移值
        dstOff = 0xFF & (self._square54Plus221(tags[15]) * srcOff)
        commentOff = (tags[12] * 256 + tags[13]) % 32000 + 767

        # 基本掩码
        arg0 = tags[3]
        # 密钥 = 前段密钥 | (后段密钥 & 基本掩码)
        args = [tags[8 + i]|(tags[12 + i] & arg0) for i in range(4)]

        # 密钥流 = 密钥 & 密钥流掩码
        encStream = [0xFF & (args[i % 4] & ord(encStreamMask[i])) for i in range(32)]

        # 返回一个 namedtuple 对象
        encrypt = Encryption(encStream, pieceOff, srcOff, dstOff, commentOff)

        return encrypt


    def _readResult(self, datas):
        result = datas[0x33]

        return result

    def _readType(self, datas):
        _type = datas[0x40]

        return _type

    # XQF 的坐标为左下为原点，转为左上为起点，向右下方向为正
    # 转为 一位矩阵的Index
    def _xqfPosToIndex(self, pos):
        x, y = int(pos / 10), int(pos % 10)
        # 转为左上为起点，向右下方向为正
        y = 9-y

        # 转位16 x 16 棋盘
        x += RANK_LEFT
        y += RANK_TOP

        return COORD_XY(x,y)

    def _readSquares(self, buff, encrypt):
        if self._readType(buff) < 2:
            # 全局或者开局
            return squaresFromInitFen()

        # 32 个棋子信息
        datas = buff[0x10:0x10+32]

        # 如果是中局或者排局，那么根据"xqfhd.szPiecePos[32]"的内容摆放局面
        piecePos = [0xFF for i in range(32)]
        if self._readVersion(buff) < 12:
            for i in range(32):
                piecePos[i] = 0xFF & (datas[i] - encrypt.pieceOff)
        else:
            # 当版本号达到12时，还要进一步解密局面初始位置
            for i in range(32):
                piecePos[(encrypt.pieceOff + 1 + i) % 32] = 0xFF & (datas[i] - encrypt.pieceOff)

        squares = [0 for i in range(256)]
        for i in range(32):
            if piecePos[i] < 90:
                index = self._xqfPosToIndex(piecePos[i])
                squares[index] = cpcXqf2Piece[i]

        return squares

    def _decrypt(self, datas, encStream, encIndex):
        buff = [0 for i in range(len(datas))]

        for i in range(len(datas)):
            buff[i] = 0xFF & (datas[i] - encStream[encIndex])
            encIndex = (encIndex + 1) % 32;

        return buff, encIndex

    def _buildMoves(self, datas, encrypt, qipu):
        xqfVer = self._readVersion(datas)

        def byte2Int(b):
            return (b[0] << 0) | (b[1] << 8) | (b[2] << 16) | (b[3] << 24)

        pos = 0x400
        encIndex = 0
        commentLen = 0

        hasNext = True
        moveObj = qipu.moveRoot

        firstMove = True # xqf 第一招为空招

        while hasNext:
            _from, _to = 0, 0

            if xqfVer < 11:
                t = datas[pos:pos+8]
                pos += 8

                _from, _to = t[0], t[1]
                hasNext = bool(t[2] & 0xf0)
                commentLen = byte2Int(t[4:])
            else:
                mv, encIndex = self._decrypt(datas[pos:pos+4], encrypt.encStream, encIndex)
                pos += 4

                _from, _to = mv[0], mv[1]
                hasNext = bool(mv[2] & 0x80)

                if ((mv[2] & 0x20) != 0):
                    ls, encIndex = self._decrypt(datas[pos:pos+4], encrypt.encStream, encIndex)
                    pos += 4

                    commentLen = byte2Int(ls)
                    commentLen -= encrypt.commentOff
                else:
                    commentLen = 0

            comment = ""
            if commentLen > 0:
                commontBytes, encIndex = self._decrypt(datas[pos:pos+commentLen], encrypt.encStream, encIndex)
                pos += commentLen

                comment = bytes(commontBytes).decode("gbk")

            if firstMove:
                firstMove = False
                moveObj.comment = comment
            else:
                _from = self._xqfPosToIndex(0xFF & (_from - 24 - encrypt.srcOff))
                _to = self._xqfPosToIndex(0xFF & (_to - 32 - encrypt.dstOff))

                nextMoveObj = Move(move = MOVE(_from, _to))
                nextMoveObj.comment = comment

                moveObj.addNext(nextMoveObj)
                moveObj = nextMoveObj

# XQF棋谱写
class XQFWriter(XQFParser):
    def __init__(self):
        pass

    def write(self, file_path, qipu):
        pass

