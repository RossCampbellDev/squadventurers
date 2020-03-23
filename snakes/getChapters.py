#!/usr/bin/env python3
import os, sys, getopt, json, re

def getChapters(fileIn, fileOut):
    chapter = 1
    copyNextLine = False
    chapters = []

    with open(fileIn, "r") as f:
        for line in f:
            if copyNextLine:
                chapters.append(line)

            if "chapter" in line.lower():
                copyNextLine = True
            else:
                copyNextLine = False

    f = open(fileOut, "w")

    for c in chapters:
        if len(c) > 5:
            chapter += 1
            f.write(c)

    f.close()
    print("Done!")


def main(args):
    usage = "getChapters -h -f <input file> -o <output file>"

    opts,args = getopt.getopt(args, 'hf:o:')
    for opt, arg in opts:
        if opt == "-h":
            print(usage)
            sys.exit(2)
        elif opt == "-f":
            if not os.path.isfile(arg):
                print("Error, missing input plaintext file")
                print(usage)
                sys.exit(2)
            else:
                fileIn = arg
        elif opt == "-o":
            fileOut = arg

    getChapters(fileIn, fileOut)

if __name__ == "__main__":
    main(sys.argv[1:])

