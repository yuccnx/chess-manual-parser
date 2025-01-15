#-*- coding: UTF-8 -*-
'''
 作者：云中买马
 公众号：编程想法
 博客：https://blog.yuccn.net
 邮箱：yuccnx@gmail.com
 代码功能：pgn 读写解析器

 格式参考 https://www.xqbase.com/protocol/cchess_pgn.htm
'''

from data import *
from fen_tool import *

def _toColumn(where):
    i = "九八七六五四三二一".find(where)
    if i != -1:
        return RANK_LEFT + i

    i = "123456789".find(where)
    if i != -1:
        return RANK_LEFT + i

    # 不应该走到这
    raise Exception('无效编号')

def _nameToKey(name):
    piecesKeys = {
        "帅将":PIECE_KING,
        "士仕":PIECE_ADVISOR,
        "相象":PIECE_BISHOP,
        "马":PIECE_KNIGHT,
        "车":PIECE_ROOK,
        "炮包砲":PIECE_CANNON,
        "兵卒":PIECE_PAWN,
    }

    if k, v in piecesKeys.items():
        if name in k:
            return v

    # 不应该走到这
    raise Exception('无效棋子')

def _findPieceByColumn(piece, squares, column):
    checkPos = 48 + column
    for i in range(10):
        if piece == squares[startPos]:
            return startPos

        startPos += 16

    # 不应该走到这
    raise Exception('没找到该子')

# Pgn棋谱读取
class PgnReader():
    # 车三进一 这种 转为移动数据
    def strToMove(self, s, squares):
        assert(len(s) == 4)
        isRed = False
        if s[3] in "一二三四五六七八九":
            isRed = True

        if s[1] in "123456789一二三四五六七八九":
            key = _nameToKey(s[0])
            piece = key | PIECE_RED if isRed else key | PIECE_BLACK
            column = _toColumn(s[1])

            _from = _findPieceByColumn(piece, squares, column)
            if piece in [PIECE_KING, PIECE_ROOK, PIECE_CANNON, PIECE_PAWN]:
                # 走直线的



    def read(self, file_path):
        pass

# Pgn棋谱写
class PgnWriter():
    def __init__(self):
        self.buff = ""


    def addLabel(self, label, val):
        self.buff += "[%s \"%s\"]\n" % (label, val)

    def isRedMove(self, sq, move):
        _from = SRC(move._move)

        return (sq[_from] & COLOR_MARK) == PIECE_RED

    def addComment(self, comment):
        if len(comment) == 0:
            return

        comment = comment.replace("{", "<")
        comment = comment.replace("}", ">")
        comment = comment.replace("(", "<")
        comment = comment.replace(")", ">")
        self.buff += "{%s}\n" % comment

        return


    def addMoves(self, qipu):
        self.addComment(qipu.moveRoot.comment)
        if len(qipu.moveRoot.nexts) == 0:
            return

        squares = [ i for i in qipu.squares]

        move = qipu.moveRoot
        step = 1

        # 分割符只能是空格、制表符或换行符 \r \n \t " "
        while len(move.nexts) > 0:
            move = move.nexts[0]
            if step % 2 == 1: # 单数时候，写上编号
                self.buff += "%d." % int((step+1) / 2)
                # 变成黑的在前面了，大一个空格
                if not self.isRedMove(squares, move):
                    self.buff += "  "
                    step += 1

            _mv = move._move

            self.buff += " " + mvToCn(_mv, squares)
            if step % 2 == 0:
                self.buff += "\n"

            if len(move.comment) != 0:
                if self.buff[-1] != "\n":
                    self.buff += "\n"
                self.addComment(move.comment)

            DO_MOVE(squares, SRC(_mv), DST(_mv))
            step += 1

    def write(self, file_path, qipu):
        self.addLabel("Game", "Chinese Chess")
        self.addLabel("Event", qipu.gameName)
        self.addLabel("Site", qipu.gamePlace)
        self.addLabel("Date", qipu.gameDate)
        self.addLabel("Red", qipu.redName)
        self.addLabel("Black", qipu.blackName)
        Results = {0:"*", 1:"1-0", 2:"0-1", 3:"1/2-1/2"}
        self.addLabel("Result", Results.get(qipu.result, "*"))
        self.addLabel("Annotator", qipu.author)
        self.addLabel("Time", qipu.timeRule)
        turnRed = True
        if len(qipu.moveRoot.nexts) > 0:
            turnRed = self.isRedMove(qipu.squares, qipu.moveRoot.nexts[0])

        self.addLabel("FEN", squaresToFen(qipu.squares, turnRed))
        self.addMoves(qipu)

        if self.buff[-1] != "\n":
            self.buff += "\n "
        self.buff += Results.get(qipu.result, "*")

        print(self.buff)

        file = open(file_path, mode="wb")
        file.write(self.buff.encode("gbk")) # 用u8 有些软件会打不开
