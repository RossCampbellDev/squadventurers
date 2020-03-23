#!/usr/bin/env python3
import os, sys, getopt, json, re



def divide(fileIn, pageSize):
    pageNo = 1
    book = []

    # read the input file as bytes and while bytes remain, create page JSONs
    with open(fileIn, "rb") as f:    
        currentPage = f.read(pageSize)

        while currentPage != b"":
            thisPage = {"pageNo":str(pageNo),"pageText":currentPage.decode('utf8')}
            book.append(thisPage)

            # step to next 'page'
            pageNo += 1
            currentPage = f.read(pageSize)
    
    # return all pages as JSON objects
    jsonResult = json.dumps(book)
    return jsonResult




def chapterfy(fileIn):
    chapters = []

    with open(fileIn, "r", encoding="utf-8") as f:
        for line in f:
            print(line)

    #chapters = wholeFile.split("Chapter")
    #chapters = ["Chapter" + c for c in chapters]

    #return chapters



def main(args):
    usage = "jsonify -h -f <input file> [-z <page size in bites]"
    pageSize = 1024 # default size of a page in bytes, can be modified

    opts,args = getopt.getopt(args, 'hf:z:')
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
        elif opt == "-z":
            if arg.isdigit():
                pageSize=int(arg)
            else:
                print("Error, -z argument must be an integer")
                sys.exit(2)

    #bk = chapterfy(fileIn)
    #print(bk)
    bk = divide(fileIn, pageSize)
    print(bk)



if __name__ == "__main__":
    main(sys.argv[1:])
