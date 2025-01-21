#-*- coding: UTF-8 -*-

import os
import sys

from converter import *

def printUsage():
    print("支持 pgn、xqf、ubb 等格式互转：")
    print("xqf 转 pgn 用法: python3 main.py file.xqf file.pgn")
    print("xqf 转 ubb 用法: python3 main.py file.xqf file.ubb")
    print("其他同理。")

def parseParam():
    argv = sys.argv
    if len(argv) != 3:
        printUsage()
        exit(0)

    inFile = argv[1]
    outFile = argv[2]

    return inFile, outFile

def main():
    inFile, outFile = parseParam()

    convert(inFile, outFile)

if __name__ == '__main__':
    main()
