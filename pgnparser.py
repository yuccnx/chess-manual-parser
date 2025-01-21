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

# 获取sq 的y 坐标
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

    for k, v in piecesKeys.items():
        if name in k:
            return v

    # 不应该走到这
    raise Exception('无效棋子')

# 再 column 列 查找 piece
def _findPiecePosByColumn(piece, squares, column):
    startPos = 48 + column
    for i in range(10):
        if piece == squares[startPos]:
            return startPos

        startPos += 16

    # 不应该走到这
    raise Exception('没找到该子')


# from：原位置
# act : 进、退、平
# where：中文一到九或者数字1-9
def _toPos(piece, _from, act, where):
    if act == "平":
        # 横着走，y 相同，x 变化
        return COORD_XY(_toColumn(where), RANK_Y(_from))

    symbol = 1
    if (isRed(piece) and act == "进") or (not IS_BLACK(piece) and act == "退"):
        symbol *= -1

    pieceKey = piece & 0x07
    if pieceKey in [PIECE_KING, PIECE_ROOK, PIECE_CANNON, PIECE_PAWN]:
        i = "一二三四五六七八九".find(where)
        if i == -1:
            i = "123456789".find(where)
            assert(i != -1)
        i += 1

        # 竖着走直线的, x 不变，变y，每变动伊格变动 16
        return _from + (i * symbol * 16)

    # 到这，就是 斜着走的子了。
    toX = _toColumn(where)

    if pieceKey == PIECE_ADVISOR: # 士
        return COORD_XY(toX, RANK_Y(_from) + 16 * symbol)

    if pieceKey == PIECE_BISHOP: # 象
        return COORD_XY(toX, RANK_Y(_from) + 32 * symbol)

    if pieceKey == PIECE_KNIGHT: # 马
        yOffset = 32 if abs(toX - RANK_X(_from)) == 1 else 16

        return COORD_XY(toX, RANK_Y(_from) + yOffset * symbol)

    # 异常
    raise Exception('招法错误')

# Pgn棋谱读取
class PgnReader():
    # 车三进一 这种 转为移动数据
    def _cnStrToMove(self, s, squares):
        assert(len(s) == 4)
        isRed = False
        if s[3] in "一二三四五六七八九":
            isRed = True


        if s[1] in "123456789一二三四五六七八九":
            # "炮二平五" 形式
            key = _nameToKey(s[0])
            piece = key | PIECE_RED if isRed else key | PIECE_BLACK
            column = _toColumn(s[1])

            _from = _findPiecePosByColumn(piece, squares, column)
            _to = _toPos(piece, _from, s[2], s[3])



    def read(self, file_path):
        pass


    # [Format "WXF"] (WXF纵线格式)
    # [Format "ICCS"] ICCS(ICCS坐标格式)
    # [Format "Chinese"] # 默认 中文标记格式

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
        self.addLabel("Format", "Chinese")
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
