#-*- coding: UTF-8 -*-

import os
import sys

from parser import *
from data import *

def printUsage():
    print("usage: python3 main.py xqf-file pgn-file")

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

    qipu = QIPU()
    reader_from_path(inFile).read(inFile, qipu)
    print(qipu)
    writer_from_path(outFile).write(outFile, qipu)


    print("from:%s to :%s finish!" % (inFile, outFile))

if __name__ == '__main__':
    main()
