#-*- coding: UTF-8 -*-

from data import *
from fen_tool import *


def dongpingMoveStrToMoves(s):
    result = []
    i = 0
    while i < len(s)-3:
        mvStr = s[i:i+4]
        fromX = int(mvStr[0])+RANK_LEFT
        fromY = int(mvStr[1])+RANK_TOP
        toX = int(mvStr[2])+RANK_LEFT
        toY = int(mvStr[3])+RANK_TOP

        result.append((COORD_XY(fromX, fromY), COORD_XY(toX, toY)))

        i += 4

    return result

class DPparser():
    def __init__(self):
        self.file = None

# 东萍棋谱读取器
class DPReader(DPparser):
    def __init__(self):
        pass

    def read(self, file_path, qipu):
        self.file = open(file_path, 'rb')

# 东萍棋谱写
class DPWriter(DPparser):
    def __init__(self):
        pass

    def write(self, file_path, qipu):
        pass
