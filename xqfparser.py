#-*- coding: UTF-8 -*-

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

class XQFParser():
    def __init__(self):
        self.file = None

# XQF棋谱读取器
class XQFReader(XQFParser):
    def __init__(self):
        self.xqfVer = 10

        # XQF 版本11 之后会加密，所以带有加密字段偏移
        self.encStream = [0 for i in range(32)]
        self.pieceOff = 0    # 局面初始位置的加密偏移值
        self.srcOff = 0      # 着法起点的加密偏移值
        self.dstOff = 0      # 着法终点的加密偏移值
        self.commentOff = 0  # 注释的加密偏移值

    def _square54Plus221(self, x):
        return x * x * 54 + 221

    # 读取字符串块，“第一个byte 是程度，后面是字符串内容” 的数据
    # [len][str……]
    def _readStrBlock(self, pos, assertMaxLen):
        self.file.seek(pos)
        length = self.file.read(1)[0]
        assert(length <= assertMaxLen)
        self.file.seek(pos+1)
        return self.file.read(length).decode("gbk")


    def read(self, file_path, qipu):
        self.file = open(file_path, 'rb')

        # 读取标记
        self._readFlag()
        # 版本
        self._readVersion()
        # 读取完版本信息，便可读取加密信息
        self._readEncStream()
        # 结果
        self._readResult(qipu)
        # 类型
        _type = self._readType(qipu)
        # 读取标题
        qipu.title = self._readStrBlock(0x50, 63)
        qipu.gameName = self._readStrBlock(0xD0, 63)
        qipu.gameDate = self._readStrBlock(0x110, 15)
        qipu.gamePlace = self._readStrBlock(0x120, 15)
        qipu.redName = self._readStrBlock(0x130, 15)
        qipu.blackName = self._readStrBlock(0x140, 15)
        qipu.timeRule = self._readStrBlock(0x150, 63)
        qipu.redTime = self._readStrBlock(0x190, 15)
        qipu.blackTime = self._readStrBlock(0x1A0, 15)
        self.commenter = self._readStrBlock(0x1D0, 15)
        self.author = self._readStrBlock(0x1E0, 15)

        # 初始局面信息
        self._readSquares(qipu, _type)

    def _readFlag(self):
        # 标记 在0开始，
        self.file.seek(0)

        flag = self.file.read(2).decode('gbk')  # 读取2个字节
        print("flag:" + flag)
        assert(flag == "XQ")

        return flag

    def _readVersion(self):
        self.file.seek(2)
        version = self.file.read(1)[0]
        print("version:", version)
        self.xqfVer = version

        return version

    def _readEncStream(self):
        # 参考 https://github.com/xqbase/eleeye/blob/master/XQFTOOLS/xqf2pgn.cpp#L60
        if self.xqfVer < 11:
            return
        self.file.seek(0)
        tags = self.file.read(16)

        # 局面初始位置的加密偏移值
        self.pieceOff = 0xFF & (self._square54Plus221(tags[13]) * tags[13])
        # 着法起点的加密偏移值
        self.srcOff = 0xFF & (self._square54Plus221(tags[14]) * self.pieceOff)
        # 着法终点的加密偏移值
        self.dstOff = 0xFF & (self._square54Plus221(tags[15]) * self.srcOff)
        self.commentOff = (tags[12] * 256 + tags[13]) % 32000 + 767

        print(self.pieceOff, self.srcOff, self.dstOff, self.commentOff)

        # 基本掩码
        arg0 = tags[3]
        # 密钥 = 前段密钥 | (后段密钥 & 基本掩码)
        args = [0 for i in range(4)]
        for i in range(4):
            args[i] = tags[8 + i] | (tags[12 + i] & arg0)

        # 密钥流 = 密钥 & 密钥流掩码
        for i in range(32):
            self.encStream[i] = 0xFF & (args[i % 4] & ord(encStreamMask[i]))


    def _readResult(self, qipu):
        self.file.seek(0x33)
        result = self.file.read(1)[0]
        addr = [RESULT_UNKNOWN, RESULT_WIN_RED, RESULT_WIN_BLACK, RESULT_PEACE]
        qipu.result = addr[result]

        return result

    def _readType(self, qipu):
        self.file.seek(0x40)
        _type = self.file.read(1)[0]
        addr = [TYPE_FULL, TYPE_START, TYPE_MIDDLE, TYPE_END]
        qipu.type = addr[_type]

        return _type

    def _readSquares(self, qipu, _type):
        if _type < 2:
            # 全局或者开局
            qipu.squares = squaresFromInitFen()
            return

        # 32 个棋子信息
        self.file.seek(0x10)
        datas = self.file.read(32)

        # 如果是中局或者排局，那么根据"xqfhd.szPiecePos[32]"的内容摆放局面
        piecePos = [0xFF for i in range(32)]
        if self.xqfVer < 12:
            for i in range(32):
                piecePos[i] = 0xFF & (datas[i] - self.pieceOff)
        else:
            # 当版本号达到12时，还要进一步解密局面初始位置
            for i in range(32):
                piecePos[(self.pieceOff + 1 + i) % 32] = 0xFF & (datas[i] - self.pieceOff)

        for i in range(32):
            if piecePos[i] < 90:
                # XQF 坐标从 坐下开始，往右上为正
                x = int(piecePos[i] / 10)
                y = int(piecePos[i] % 10)

                # 转为左上为起点，向右下方向为正
                y = 9-y

                # 转位16 x 16 棋盘
                x += RANK_LEFT
                y += RANK_TOP

                qipu.squares[COORD_XY(x,y)] = cpcXqf2Piece[i]


# XQF棋谱写
class XQFWriter(XQFParser):
    def __init__(self):
        pass

    def write(self, file_path, qipu):
        pass

