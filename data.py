#-*- coding: UTF-8 -*-


TYPE_FULL   = 0 # 全局
TYPE_START  = 1 # 布局
TYPE_MIDDLE = 2 # 中局
TYPE_END    = 3 # 残局

RESULT_UNKNOWN   = 0 # 未知
RESULT_WIN_RED   = 1 # 红胜
RESULT_WIN_BLACK = 2 # 黑胜
RESULT_PEACE     = 3 # 和棋


class QIPU():
    def __init__(self):
        # 记谱时间
        self.adddate = ""
        self.title = ""
        self.type = TYPE_FULL
        self.result = RESULT_UNKNOWN
        self.timerule = ""   # 用时规则
        self.redTime = ""    # 红方用时
        self.blackTime = ""  # 红方用时
        self.redName = ""    # 红方名字
        self.blackName = ""  # 黑方名字

        self.squares = []    # 16 x 16
        self.comment = ""

        self.move = None

    def __str__(self):
        result = "时间:%s\n" % self.adddate
        result += "标题:%s\n" % self.title
        result += "类型:%s\n" % {0:"全局",1:"布局",2:"中局",3:"残局"}.get(self.type, "")
        result += "结果:%s\n" % {0:"未知",1:"红胜",2:"黑胜",3:"和棋"}.get(self.result, "")

        return result

class MOVE():
    def __init__(self):
        self.comment = ""

        # 真正的移动，
        self._move = 0

        # 下一招
        self.next = None

        # 变招
        self.brothers



