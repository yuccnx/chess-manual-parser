#-*- coding: UTF-8 -*-

import os
import sys

def printUsage():
    print("usage: python3 main.py xqf-file pgn-file")

def parseParam():
    argv = sys.argv
    if len(argv) < 2 or len(argv) > 3:
        printUsage()
        exit(0)

    xqfFile = argv[1]
    pgnFile = ""

    if len(argv) == 3:
        pgnFile = argv[2]
    else:
        pgnFile = xqfFile.replace(".xqf", ".pgn").replace(".XQF", ".pgn")
        if pgnFile == xqfFile:
            pgnFile = pgnFile + ".pgn"


    return xqfFile, pgnFile

def xqf2pgn(xqfFilePath, pgnFilePath):
    pass
    # with open(xqfFilePath, "rb") as xqfFile:

def main():
    xqfFile, pgnFile = parseParam()
    print("xqf-file:%s to pgn-file:%s" % (xqfFile, pgnFile))

    xqf2pgn(xqfFile, pgnFile)

if __name__ == '__main__':
    main()
