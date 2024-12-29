#-*- coding: UTF-8 -*-

from data import *

class Parser():
    def __init__(self):
        self.file = None

class DPparser(Parser):
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
        pass

    def write(self, file_path, qipu):
        pass

class XQFParser(Parser):
    def __init__(self):
        pass

# XQF棋谱读取器
class XQFReader(XQFParser):
    def __init__(self):
        pass

    def read(self, file_path, qipu):
        self.file = open(file_path, 'rb')

        # 读取标记
        self._readFlag()
        # 版本
        self._readVersion()
        # 结果
        self._readResult(qipu)
        # 类型
        self._readType(qipu)

    def _readFlag(self):
        # 标记 在0开始，
        self.file.seek(0)

        flag = self.file.read(2).decode('utf-8')  # 读取2个字节
        print("flag:" + flag)
        assert(flag == "XQ")

    def _readVersion(self):
        self.file.seek(2)
        version = self.file.read(1)[0]

        print("version:", version)

        # 确保版本号是1.x，高版本不支持解析
        assert((version - version % 10) == 10)

    def _readResult(self, qipu):
        self.file.seek(0x33)
        result = self.file.read(1)[0]
        addr = [RESULT_UNKNOWN, RESULT_WIN_RED, RESULT_WIN_BLACK, RESULT_PEACE]
        qipu.result = addr[result]

    def _readType(self, qipu):
        self.file.seek(0x40)
        _type = self.file.read(1)[0]
        addr = [TYPE_FULL, TYPE_START, TYPE_MIDDLE, TYPE_END]
        qipu.type = addr[_type]

# XQF棋谱写
class XQFWriter(XQFParser):
    def __init__(self):
        pass

    def write(self, file_path, qipu):
        pass

def reader_from_path(file_path):
    file_path = file_path.lower()
    if file_path.endswith(".xqf"):
        return XQFReader()
    elif file_path.endswith(".ubb"):
        return DPReader()

    return None

def writer_from_path(file_path):
    file_path = file_path.lower()
    if file_path.endswith(".xqf"):
        return XQFWriter()
    elif file_path.endswith(".ubb"):
        return DPWriter()

    return None
