#-*- coding: UTF-8 -*-

# 定义棋谱数据格式

TYPE_FULL   = 0 # 全局
TYPE_START  = 1 # 布局
TYPE_MIDDLE = 2 # 中局
TYPE_END    = 3 # 残局

RESULT_UNKNOWN   = 0 # 未知
RESULT_WIN_RED   = 1 # 红胜
RESULT_WIN_BLACK = 2 # 黑胜
RESULT_PEACE     = 3 # 和棋

class Move():
    def __init__(self, move = 0, isRoot = False):
        self.isRoot = isRoot
        self.comment = ""

        # 真正的移动，
        self._move = move

        # 下一招
        self.nexts = [] # MOVE 结构

    def addNext(self, next):
        self.nexts.append(next)


class Qipu():
    def __init__(self):
        self.addDate = "" # 记谱时间
        self.title = "" # 标题
        self.type = TYPE_FULL
        self.result = RESULT_UNKNOWN
        self.gameName = ""
        self.gameDate = "" # 游戏时间
        self.gamePlace = ""
        self.timeRule = ""   # 用时规则
        self.redTime = ""    # 红方用时
        self.blackTime = ""  # 黑方用时
        self.redName = ""    # 红方棋手
        self.blackName = ""  # 黑方棋手

        self.squares = [0 for i in range(256)]    # 16 x 16 fen_tool 里面的数据格式
        self.commenter = ""
        self.author = "" # 棋谱制作者

        # 招法，注意：第一招为空招，self.rootMove.nexts 才是真正的招法
        # 目的：方便记录第一招 有变招情况
        self.moveRoot = Move(isRoot = True)

    def __str__(self):
        result = "标题:%s\n" % self.title
        result += "记谱时间:%s\n" % self.addDate
        result += "时间:%s\n" % self.gameDate
        result += "地点:%s\n" % self.gamePlace
        result += "名称:%s\n" % self.gameName
        result += "类型:%s\n" % {0:"全局",1:"布局",2:"中局",3:"残局"}.get(self.type, "")
        result += "红方:%s\n" % self.redName
        result += "黑方:%s\n" % self.blackName
        result += "结果:%s\n" % {0:"未知",1:"红胜",2:"黑胜",3:"和棋"}.get(self.result, "")
        result += "用时规则:%s\n" % self.timeRule
        result += "红方用时:%s\n" % self.redTime
        result += "黑方用时:%s\n" % self.blackTime
        result += "棋谱评说者:%s\n" % self.commenter
        result += "棋谱作者:%s\n" % self.author

        return result



