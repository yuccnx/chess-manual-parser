#-*- coding: UTF-8 -*-
'''
 作者：编程想法
 公众号：编程想法
 博客：https://blog.yuccn.net
 邮箱：yuccnx@gmail.com
 代码功能：东萍棋谱 读写解析器
'''

from data import *
from fen_tool import *


def _DPMoveStrToMoves(s):
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

# DhtmlXQ_move_x_y_z
# x 为 哪个分支下的变招
# y 为 开局到此，第几步
# z 为当前变招号
def _toMoveKey(parentBranchIndex, stepCount, branchIndex):
    if branchIndex == 0:
        return "DhtmlXQ_movelist"

    return "DhtmlXQ_move_%d_%d_%d" % (parentBranchIndex, stepCount, branchIndex)

# DhtmlXQ_commentx_y
# x分支号，y 第几步的说明
def _toCommentKey(branchIndex, stepCount):
    if branchIndex == 0:
        return "DhtmlXQ_comment%d" % stepCount
    return "DhtmlXQ_comment%d_%d" % (branchIndex, stepCount)

def _mvToStr(_mv):
    _from, _to = SRC(_mv), DST(_mv)
    _fromX, _fromY = RANK_X(_from) - RANK_LEFT, RANK_Y(_from) - RANK_TOP
    _toX, _toY = RANK_X(_to) - RANK_LEFT, RANK_Y(_to) - RANK_TOP

    return "%d%d%d%d" % (_fromX, _fromY, _toX, _toY)

class DPparser():
    def __init__(self):
        pass

# 东萍棋谱读取器
class DPReader(DPparser):
    def __init__(self):
        pass

    def read(self, file_path, qipu):
        self.file = open(file_path, 'rb')

# 东萍棋谱写
class DPWriter(DPparser):
    def __init__(self):
        self.buff = ""

    def _buildTitle(self, qipu):
        if qipu.title:
            return qipu.title

        if qipu.redName and qipu.blackName and qipu.result in (1,2,3):
            resultsStr = ["", " 先胜 ", " 先负 ", " 先和 "]
            return qipu.redName + resultsStr[qipu.result] + qipu.blackName

        return ""


    def _buildMoveAndMoveComment(self, qipu):
        branchCount = 0
        moveVals, commentVals = [], [] # [(k,v) ……]

        def _build(move, parentIndex, stepCount, currentIndex):
            nonlocal branchCount
            nonlocal moveVals
            nonlocal commentVals

            # 分两部分处理
            # 1 处理 nexts[0] 也就是 嫡系 数据;2 处理非 nexts[1:] 也就是 非嫡系 数据

            # 根是空招，不记录
            mvStr = "" if move.isRoot else _mvToStr(move._move)
            if move.comment:
                k = _toCommentKey(currentIndex, stepCount)
                v = move.comment.replace("\r", "||").replace("\n", "||")
                commentVals.append((k, v))

            nextStepCount = stepCount
            while len(move.nexts) > 0:
                # 嫡系
                first = move.nexts[0]
                others = move.nexts[1:]
                nextStepCount += 1

                mvStr += _mvToStr(first._move)
                if first.comment:
                    k = _toCommentKey(currentIndex, nextStepCount)
                    v = first.comment.replace("\r", "||").replace("\n", "||")
                    commentVals.append((k, v))

                # 非嫡系
                for other in others:
                    branchCount += 1 # 多一个分支
                    _build(other, currentIndex, nextStepCount, branchCount)

                move = first

            moveKey = _toMoveKey(parentIndex, stepCount, currentIndex)
            moveVals.append((moveKey, mvStr))

        _build(qipu.moveRoot, 0, 0, 0)


        return moveVals + commentVals


    def _buildSquares(self, qipu):
        positions = ["99"] * 32
        piecesIndex = {
          13:[0,8], # 红车
          12:[1,7], # 红马
          11:[2,6], # 红相
          10:[3,5], # 红士
          9:[4],   # 红帅
          14:[9,10],# 红炮
          15:[11,12,13,14,15],# 红兵

          21:[16,24], # 黑车
          20:[17,23], # 黑马
          19:[18,22], # 黑相
          18:[19,21], # 黑士
          17:[20],   # 黑将
          22:[25,26],# 黑炮
          23:[27,28,29,30,31],# 黑卒
        }

        for i in PIECES_POS:
            piece = qipu.squares[i]
            if piece == 0:
                continue

            x, y = RANK_X(i)-RANK_LEFT, RANK_Y(i)-RANK_TOP
            pos = piecesIndex[piece].pop()
            positions[pos] = "%d%d" % (x, y)

        return "".join(positions)


    def write(self, file_path, qipu):
        self.buff = ""
        file = open(file_path, "w")

        self._addDPStart()
        self._addDPFields("DhtmlXQ_ver", "www_dpxq_com")
        self._addDPFields("DhtmlXQ_init", "500,350")
        self._addDPFields("DhtmlXQ_binit", self._buildSquares(qipu))
        self._addDPFields("DhtmlXQ_adddate", qipu.gameDate)
        self._addDPFields("DhtmlXQ_title", self._buildTitle(qipu))
        self._addDPFields("DhtmlXQ_editdate", qipu.adddate)
        self._addDPFields("DhtmlXQ_event", qipu.gameName)
        self._addDPFields("DhtmlXQ_red", qipu.redName)
        self._addDPFields("DhtmlXQ_black", qipu.blackName)
        self._addDPFields("DhtmlXQ_place", qipu.gamePlace)
        self._addDPFields("DhtmlXQ_timerule", qipu.timeRule)
        self._addDPFields("DhtmlXQ_owner", qipu.author)

        vals = self._buildMoveAndMoveComment(qipu)
        for item in vals:
            self._addDPFields(item[0], item[1])

        results = {0:"未知", 1:"红胜", 2:"黑胜", 3:"和棋"}
        self._addDPFields("DhtmlXQ_result", results.get(qipu.result, "未知"))

        types = {0:"全局",1:"布局",2:"中局",3:"残局"}
        self._addDPFields("DhtmlXQ_type", types.get(qipu.type, ""))

        self._addDPFields("DhtmlXQ_refer", "https%3A//blog.yuccn.net")
        self._addDPEnd()

        file.write(self.buff)

    def _addDPFields(self, field, val):
        if not val:
            return

        datas = "[%s]%s[/%s]\r\n" % (field, val, field)
        self.buff += datas


    def _addDPStart(self):
        self.buff += "[DhtmlXQ]\r\n"

    def _addDPEnd(self):
        self.buff += "[/DhtmlXQ]\r\n"

