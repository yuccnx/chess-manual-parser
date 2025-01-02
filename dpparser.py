#-*- coding: UTF-8 -*-

from data import *
from fen_tool import *


def DPMoveStrToMoves(s):
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

        if qipu.redName and qipu.blackName:
            if qipu.result == 1:
                return qipu.redName + " 先胜 " + qipu.blackName
            elif qipu.result == 2:
                return qipu.redName + " 先负 " + qipu.blackName
            elif qipu.result == 3:
                return qipu.redName + " 先和 " + qipu.blackName

        return ""

    def _buildMoveAndMoveComment(self, qipu):
        commentRoot = qipu.moveRoot
        vals = {}

        if len(commentRoot.nexts) == 0:
            return vals

        def _mvToStr(_mv):
            _from, _to = SRC(_mv), DST(_mv)
            _fromX, _fromY = RANK_X(_from) - RANK_LEFT, RANK_Y(_from) - RANK_TOP
            _toX, _toY = RANK_X(_to) - RANK_LEFT, RANK_Y(_to) - RANK_TOP

            return "%d%d%d%d" % (_fromX, _fromY, _toX, _toY)


        def _build(move):
            mvstr = _mvToStr(move._move)

            while len(move.nexts) > 0:
                move = move.nexts[0]
                mvstr += _mvToStr(move._move)

            return mvstr

        vals["DhtmlXQ_movelist"] = _build(commentRoot.nexts[0])

        return vals


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
        for k, v in vals.items():
            self._addDPFields(k, v)

        comment = qipu.comment + qipu.moveRoot.comment
        comment = comment.replace("\r", "||").replace("\n", "||")
        self._addDPFields("DhtmlXQ_comment0", comment)

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

