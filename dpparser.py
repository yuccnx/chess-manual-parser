#-*- coding: UTF-8 -*-
'''
 作者：云中买马
 公众号：编程想法
 博客：https://blog.yuccn.net
 邮箱：yuccnx@gmail.com
 代码功能：东萍棋谱 读写解析器
'''

from data import *
from fen_tool import *


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

def _strToIndex(s):
    return COORD_XY(int(s[0]) + RANK_LEFT, int(s[1]) + RANK_TOP)

def _strToMove(s):
    _from = _strToIndex(s[0:2])
    _to = _strToIndex(s[2:4])

    return MOVE(_from, _to)

def _stringBetween(s, leftStr, rightStr):
    start = s.find(leftStr)
    if start == -1:
        return ""

    end = s.find(rightStr)
    if end == -1:
        return ""

    return s[start+len(leftStr):end]

# 东萍棋谱读取器
class DPReader():
    def __init__(self):
        pass

    def _readFieldVal(self, s, field):
        start = s.find("[" + field + "]")
        if start == -1:
            return ""

        end = s.find("[/" + field + "]")
        if end == -1:
            return ""

        start += len(field) + 2

        if start >= end:
            return ""

        return s[start:end]


    def _DPPosToIndex(self, pos):
        x, y = int(pos[0]), int(pos[1])
        # 转位16 x 16 棋盘
        x += RANK_LEFT
        y += RANK_TOP

        return COORD_XY(x,y)


    def _parserBInit(self, binit, qipu):
        assert(len(binit) == 64)

        qipu.squares = [0 for i in range(256)]

        pieces = [
          13, 12, 11, 10, 9, 10, 11, 12, 13, 14, 14, 15, 15, 15, 15, 15,
          21, 20, 19, 18, 17, 18, 19, 20, 21, 22, 22, 23, 23, 23, 23, 23,
        ]

        for i in range(0, len(binit), 2):
            pos = binit[i:i+2]
            if pos == "99":
                continue

            qipu.squares[self._DPPosToIndex(pos)] = pieces[int(i / 2)]


    def _extractBranch(self, datas):
        def _splitMoveKey(k):
            arr = k.split("_")
            if len(arr) != 3:
                return False, 0, 0, 0
            return True, int(arr[0]), int(arr[1]), int(arr[2])

        lines = datas.replace("\r", "\n").split("\n")

        # 抽取出走法分支数据
        _lines = []
        for line in lines:
            if line.startswith("[DhtmlXQ_move_"):
               _lines.append(line.replace("DhtmlXQ_move_", ""))

        movelist = self._readFieldVal(datas, "DhtmlXQ_movelist")
        if movelist:
            _lines.insert(0, "[0_1_0]" + movelist + "[/0_1_0]")

        # 整理为如下的一个map 方便读取处理
        branchs = {} # {index: {id:x, mv:xx, parrent_step:x, parrent_id}}
        for line in _lines:
            mk = _stringBetween(line, "[", "]")
            result, parentId, parentStep, Id =  _splitMoveKey(mk)
            if not result:
                continue

            mv = _stringBetween(line, "[%s]" % mk, "[/%s]" % mk)
            branchs[Id] = {"id":Id, "moves":mv, "parrent_step":parentStep, "parrent_id":parentId}

        return branchs


    # 整理评论列表
    def _extractComment(self, datas):
        lists = datas.replace("[DhtmlXQ_comment", "split-comment[DhtmlXQ_comment").split("split-comment")
        comments = {}
        for item in lists:
            fieldName = _stringBetween(item, "[", "]");
            if fieldName == "" or not fieldName.startswith("DhtmlXQ_comment"):
                continue

            comments[fieldName] = self._readFieldVal(datas, fieldName);

        return comments;


    def _parserMoveAndComment(self, datas, qipu):
        branchs = self._extractBranch(datas)     # 招法信息
        comments = self._extractComment(datas)   # 评论信息

        def _getMultiChange(branchs, index, step):
            changes = []
            for k, branch in branchs.items():
                if branch["parrent_id"] == index and branch["parrent_step"] == step:
                    changes.append(branch)

            return changes

        def _buildNext(branchs, comments, parentIndex, parrentStep, moveRoot):
            changes = _getMultiChange(branchs, parentIndex, parrentStep)
            if len(changes) == 0:
                return

            sorted(changes, key=lambda change: change['id'])

            others = []
            # 所有变招分支
            for change in changes:
                moveStr = change["moves"]
                index = change["id"]

                tail = moveRoot
                assert((len(moveStr) % 4) == 0)

                tailStep = parrentStep
                for i in range(0, len(moveStr), 4):
                    moveObj = Move(move = _strToMove(moveStr[i:i+4]))

                    commentID = "DhtmlXQ_comment"
                    if index == 0:
                        commentID = commentID + str(tailStep)
                    else:
                        commentID = commentID + str(index) + "_" + str(tailStep)

                    moveObj.comment = comments.get(commentID, "")
                    tail.nexts.append(moveObj)
                    tail = moveObj
                    tailStep += 1

                    # 先建设完嫡系数据，再建设非嫡系
                    if i != 0:
                        others.append((index, tailStep, tail))

                # 非嫡系的数据
                for (_index, _tailStep, _tail) in others:
                    _buildNext(branchs, comments, _index, _tailStep, _tail)

        moveRoot = qipu.moveRoot
        moveRoot.comment = comments.get("DhtmlXQ_comment0", "")

        _buildNext(branchs, comments, 0, 1, moveRoot)


    def read(self, file_path, qipu):
        file = open(file_path, 'r')
        datas = file.read()
        file.close()

        qipu.title = self._readFieldVal(datas, "DhtmlXQ_title")
        qipu.addDate = self._readFieldVal(datas, "DhtmlXQ_adddate")
        qipu.gameName = self._readFieldVal(datas, "DhtmlXQ_event")
        qipu.gameDate = self._readFieldVal(datas, "DhtmlXQ_date")
        qipu.gamePlace = self._readFieldVal(datas, "DhtmlXQ_place")
        qipu.timeRule = self._readFieldVal(datas, "DhtmlXQ_timerule")
        qipu.redTime = self._readFieldVal(datas, "DhtmlXQ_redtime")
        qipu.blackTime = self._readFieldVal(datas, "DhtmlXQ_blacktime")
        qipu.redName = self._readFieldVal(datas, "DhtmlXQ_red")
        qipu.blackName = self._readFieldVal(datas, "DhtmlXQ_black")
        qipu.author = self._readFieldVal(datas, "DhtmlXQ_author")
        binit = self._readFieldVal(datas, "DhtmlXQ_binit")
        if not binit:
            binit = "8979695949392919097717866646260600102030405060708012720323436383"

        self._parserBInit(binit, qipu)
        self._parserMoveAndComment(datas, qipu)

        _type = self._readFieldVal(datas, "DhtmlXQ_type")
        qipu.type = TYPE_FULL
        if _type == "中局":
            qipu.type = TYPE_MIDDLE
        elif _type == "残局":
            qipu.type = TYPE_END

        result = self._readFieldVal(datas, "DhtmlXQ_result")
        qipu.result = RESULT_UNKNOWN
        if result == "红胜":
            qipu.result = RESULT_WIN_RED
        elif _type == "黑胜":
            qipu.result = RESULT_WIN_BLACK
        elif _type == "和棋":
            qipu.result = RESULT_PEACE


'''
        self.squares = [0 for i in range(256)]    # 16 x 16 fen_tool 里面的数据格式
'''
# 东萍棋谱写
class DPWriter():
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

            # 根是空招，不记录
            mvStr = "" if move.isRoot else _mvToStr(move._move)
            if move.comment:
                k = _toCommentKey(currentIndex, stepCount)
                v = move.comment.replace("\r", "||").replace("\n", "||")
                commentVals.append((k, v))

            # 分两部分处理
            # 1 处理 nexts[0] 也就是 嫡系 数据;
            # 2 处理非 nexts[1:] 也就是 非嫡系 数据
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
        self._addDPFields("DhtmlXQ_adddate", qipu.addDate)
        self._addDPFields("DhtmlXQ_date", qipu.gameDate)
        self._addDPFields("DhtmlXQ_title", self._buildTitle(qipu))
        self._addDPFields("DhtmlXQ_editdate", qipu.addDate)
        self._addDPFields("DhtmlXQ_event", qipu.gameName)
        self._addDPFields("DhtmlXQ_red", qipu.redName)
        self._addDPFields("DhtmlXQ_black", qipu.blackName)
        self._addDPFields("DhtmlXQ_place", qipu.gamePlace)
        self._addDPFields("DhtmlXQ_timerule", qipu.timeRule)
        self._addDPFields("DhtmlXQ_redtime", qipu.redTime)
        self._addDPFields("DhtmlXQ_blacktime", qipu.blackTime)
        self._addDPFields("DhtmlXQ_author", qipu.author)

        results = {0:"未知", 1:"红胜", 2:"黑胜", 3:"和棋"}
        self._addDPFields("DhtmlXQ_result", results.get(qipu.result, "未知"))

        types = {0:"全局",1:"布局",2:"中局",3:"残局"}
        self._addDPFields("DhtmlXQ_type", types.get(qipu.type, ""))

        vals = self._buildMoveAndMoveComment(qipu)
        for item in vals:
            self._addDPFields(item[0], item[1])

        self._addDPFields("DhtmlXQ_generator", "https%3A//blog.yuccn.net")
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

