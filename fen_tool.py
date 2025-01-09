#-*- coding: UTF-8 -*-

RANK_TOP = 3
RANK_BOTTOM = 12
RANK_LEFT = 3
RANK_RIGHT = 11

RANK_WIDTH = 16

SQUARE_SIZE = 256

PIECE_RED   = 0x08
PIECE_BLACK = 0x10
COLOR_MARK  = 0x18

PIECE_KING    = 0x01
PIECE_ADVISOR = 0x02
PIECE_BISHOP  = 0x03
PIECE_KNIGHT  = 0x04
PIECE_ROOK    = 0x05
PIECE_CANNON  = 0x06
PIECE_PAWN    = 0x07

PIECE_KING_RED    = PIECE_RED | PIECE_KING
PIECE_ADVISOR_RED = PIECE_RED | PIECE_ADVISOR
PIECE_BISHOP_RED  = PIECE_RED | PIECE_BISHOP
PIECE_KNIGHT_RED  = PIECE_RED | PIECE_KNIGHT
PIECE_ROOK_RED    = PIECE_RED | PIECE_ROOK
PIECE_CANNON_RED  = PIECE_RED | PIECE_CANNON
PIECE_PAWN_RED    = PIECE_RED | PIECE_PAWN

PIECE_KING_BLACK    = PIECE_BLACK | PIECE_KING
PIECE_ADVISOR_BLACK = PIECE_BLACK | PIECE_ADVISOR
PIECE_BISHOP_BLACK  = PIECE_BLACK | PIECE_BISHOP
PIECE_KNIGHT_BLACK  = PIECE_BLACK | PIECE_KNIGHT
PIECE_ROOK_BLACK    = PIECE_BLACK | PIECE_ROOK
PIECE_CANNON_BLACK  = PIECE_BLACK | PIECE_CANNON
PIECE_PAWN_BLACK    = PIECE_BLACK | PIECE_PAWN

# 一维棋谱样式
'''
[
    0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0, 0, 0,
    0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0, 0, 0,
    0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0, 0, 0,
    0, 0, 0, 21, 20, 19, 18, 17, 18, 19, 20, 21, 0, 0, 0, 0,
    0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0, 0, 0,
    0, 0, 0, 0,  22, 0,  0,  0,  0,  0,  22, 0,  0, 0, 0, 0,
    0, 0, 0, 23, 0,  23, 0,  23, 0,  23, 0,  23, 0, 0, 0, 0,
    0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0, 0, 0,
    0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0, 0, 0,
    0, 0, 0, 15, 0,  15, 0,  15, 0,  15, 0,  15, 0, 0, 0, 0,
    0, 0, 0, 0,  14, 0,  0,  0,  0,  0,  14, 0,  0, 0, 0, 0,
    0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0, 0, 0,
    0, 0, 0, 13, 12, 11, 10, 9,  10, 11, 12, 13, 0, 0, 0, 0,
    0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0, 0, 0,
    0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0, 0, 0,
    0, 0, 0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0, 0, 0
 ]
'''

# 记录一维棋盘坐标，方便后续遍历使用
PIECES_POS = [
     51,52, 53, 54, 55, 56, 57, 58, 59,
     67,68, 69, 70, 71, 72, 73, 74, 75,
     83,84, 85, 86, 87, 88, 89, 90, 91,
     99,100,101,102,103,104,105,106,107,
    115,116,117,118,119,120,121,122,123,
    131,132,133,134,135,136,137,138,139,
    147,148,149,150,151,152,153,154,155,
    163,164,165,166,167,168,169,170,171,
    179,180,181,182,183,184,185,186,187,
    195,196,197,198,199,200,201,202,203,
]

_initFen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"

# 转Y 坐标
def RANK_Y(sq):
    return sq >> 4

# 转x 坐标
def RANK_X(sq):
    return sq & 15

# 转数据棋盘坐标
def COORD_XY(x, y):
    return x + (y << 4)

def DO_MOVE(squares, src, to):
    squares[to] = squares[src]
    squares[src] = 0

# 一维棋谱走法表示：低8位表示原位置，高八位表示移动到的目标位置
def MOVE(src, dst):
    return (src | (dst << 8))

def SRC(mv):
    return mv & 0xFF;

def DST(mv):
    return mv >> 8

def IS_RED(v):
    return (v & PIECE_RED) == PIECE_RED

def IS_BLACK(v):
    return (v & PIECE_BLACK) == PIECE_BLACK

# bin(111) = 7
def PIECE_VAL(v):
    return v & 7 #  & 111

def CHAR_TO_PIECE(c):
    side = 0
    if ("A" <= c and c <= "Z"):
        side = PIECE_RED
    elif ("a" <= c and c <= "z"):
        side = PIECE_BLACK

    if c == "K" or c == "k":
        return PIECE_KING | side
    if c == "A" or c == "a":
        return PIECE_ADVISOR | side
    if c == "B" or c == "E" or c == "b" or c == "e":
        return PIECE_BISHOP | side
    if c == "H" or c == "N" or c == "h" or c == "n":
        return PIECE_KNIGHT | side
    if c == "R" or c == "r":
        return PIECE_ROOK | side
    if c == "C" or c == "c":
        return PIECE_CANNON | side
    if c == "P" or c =="p":
        return PIECE_PAWN | side

    return -1

def squaresFromFen(fen):
    squares = [ 0 for i in range(SQUARE_SIZE)]

    x = RANK_LEFT
    y = RANK_TOP

    for c in fen:
        if c == " ":
            break

        if c == "/":
            x = RANK_LEFT
            y += 1
        elif "1" <= c and c <= "9":
            x += int(c)
        elif (("A" <= c and c <= "Z") or ("a" <= c and c <= "z")):
            squares[COORD_XY(x, y)] = CHAR_TO_PIECE(c);
            x += 1

        if y > RANK_BOTTOM:
            break

    return squares

def PIECE_TO_CHAR(piece):
    fenValues = [
        "", "", "", "", "", "", "", "","",
        "K", "A", "B", "N", "R", "C", "P", "",
        "k", "a", "b", "n", "r", "c", "p", "",
    ]

    if 0 <= piece and piece <= len(fenValues) - 1:
        return fenValues[piece]

    return ""

def PIECE_TO_CN_CHAR(piece):
    cnValues = [
        "", "", "", "", "", "", "", "", "",
        "帅", "士","相","马","车","炮","兵", "",
        "将", "士","象","马","车","炮","卒", "",
    ]

    if 0 <= piece and piece < len(cnValues):
        return cnValues[piece]

    return ""

def squaresToFen(sq, turnRed):
    fen = "";

    spaceCount = 0
    for i in range(len(PIECES_POS)):
        piece = sq[PIECES_POS[i]]
        if piece == 0:
            spaceCount += 1
        else:
            if spaceCount > 0:
                fen = fen + str(spaceCount)
                spaceCount = 0

            fen = fen + PIECE_TO_CHAR(piece)

        if i % 9 == 8:
            if spaceCount > 0:
                fen = fen + str(spaceCount)
                spaceCount = 0

            if i != len(PIECES_POS) - 1:
                fen = fen + "/"

    fen += " w - - 0 1" if turnRed else " b  - - 0 1"

    return fen

def squaresFromInitFen():
    return squaresFromFen(_initFen)

def posStrToPos(s):
    x = "abcdefghi".find(s[0])
    y = "9876543210".find(s[1])
    if x == -1 or y == -1:
        return 0

    return COORD_XY(x+RANK_LEFT, y+RANK_TOP)

def fenMoveStrToMove(s):
    src, dst = 0, 0
    if len(s) == 4:
        src = posStrToPos(s[:2])
        dst = posStrToPos(s[2:])

    return (src, dst)

def fensMoveStrToMoves(moveStr):
    return [fenMoveStrToMove(move) for  move in moveStr.split(" ")]


# 转成中文招法
def mvToCn(mv, squares):
    src, dst = SRC(mv), DST(mv)

    fromX, fromY = RANK_X(src) - RANK_LEFT, RANK_Y(src) - RANK_TOP
    toX, toY = RANK_X(dst) - RANK_LEFT, RANK_Y(dst) - RANK_TOP

    numcns = ["零","一","二","三","四","五","六","七","八","九"]
    nums = ["0","1","2","3","4","5","6","7","8","9"]

    pc = squares[src]
    b1 = PIECE_TO_CN_CHAR(pc)
    b2 = numcns[9-fromX] if IS_RED(pc) else nums[fromX + 1]
    b3 = "平"
    if toY != fromY:
        b3 = "进"
        if (IS_RED(pc) and toY > fromY) or (IS_BLACK(pc) and toY < fromY):
            b3 = "退"
    b4 = ""

    v = PIECE_VAL(pc)
    if ((v == PIECE_ADVISOR or v == PIECE_BISHOP or v == PIECE_KNIGHT) or toY == fromY):
        # 走斜线（象，士，马）的子，或者 横着走的时候，用 x 位置计算
        b4 = numcns[9-toX] if IS_RED(pc) else nums[toX + 1]
    else:
        # 其他走直线
        b4 = numcns[abs(toY-fromY)] if IS_RED(pc) else nums[abs(toY-fromY)]

    if v == PIECE_ADVISOR or v == PIECE_BISHOP or v == PIECE_KING:
        # 士、象、将 不用考虑前中后问题
        return b1 + b2 + b3 + b4;

    # 在同x位置上的同子的y 位置
    ySamePieces = []
    for y in range(10):
        if squares[COORD_XY(RANK_X(src), y + RANK_TOP)] == pc:
            ySamePieces.append(y)

    if len(ySamePieces) == 1:
        return b1 + b2 + b3 + b4

    # 多个相同子竖着并排情况
    b2 = PIECE_TO_CN_CHAR(pc)
    sameCount = len(ySamePieces)
    if sameCount == 2:
        b1 = "后"
        if (IS_RED(pc) and (fromY == ySamePieces[0])) or (IS_BLACK(pc) and (fromY == ySamePieces[1])):
            b1 = "前"
    elif sameCount == 3:
        b1 = "中"
        if fromY != ySamePieces[1]:
            b1 = "后"
            if (IS_RED(pc) and (fromY == ySamePieces[0])) or (IS_BLACK(pc) and (fromY == ySamePieces[2])):
                b1 = "前"
    elif sameCount == 4 or sameCount == 5:
        index = ySamePieces.index(fromY) + 1
        if (IS_RED(pc)):
            index = sameCount-index;

        b1 = numcns[index+1]

    return b1 + b2 + b3 + b4
