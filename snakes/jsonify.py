#!/usr/bin/python
import json, sys, getopt, os

pageSize = 2600

def jsonify(f, page):
    start = True
    absoluteCount = 1
    pageNumber = 1
    chapterNumber = 1
    carryOver = ""
    thisPage = {}
    pagesDictionary = []
    newChapter = False

    # while there are characters remaining in the file
    while page != "":
	# if its the start of the entire thing no need to check anything, just create the JSON page
        # page { chapterNumber:1, pageNumber:1, pageText:"hello there" }
	if start:
            start = False
            # find the last space that occurs, and end the page immediately before it (find last whole word within 1kb)
            lastChar = page.rfind(" ")
            pageText = carryOver + page[:lastChar]

            # add pageText to JSON object here
            thisPage["absoluteCount"] = absoluteCount
            thisPage["chapterNum"] = str(chapterNumber)
            thisPage["pageNum"] = str(pageNumber)
            thisPage["pageText"] = pageText.replace("\r\n","\n").replace("\n","<br/>") + "<span class=next>&nbsp;... next page</span>"
            pagesDictionary.append(thisPage.copy())

            # then add any remaining characters to the next page
            carryOver = page[lastChar:pageSize]
	else:
            # increment the absolute count - from 1 to number of pages total
            absoluteCount += 1

            # if its not the first page, increment page count
            pageNumber += 1
            
            # if there is a new chapter, end the current page and start a new one
            pos = page.find("CHAPTER ")
            if pos > -1:
                newChapter = True
            # if there isn't a new chapter, read page normally
            else:
                lastChar = page.rfind(" ")
            
            pageText = carryOver + page[:lastChar]

            # add to json
            thisPage["absoluteCount"] = absoluteCount
            thisPage["chapterNum"] = str(chapterNumber)
            thisPage["pageNum"] = str(pageNumber)
            thisPage["pageText"] = pageText.replace("\r\n","\n").replace("\n","<br/>") + "<span class=next>&nbsp;... next page</span>"
            pagesDictionary.append(thisPage.copy())

            if newChapter:
                lastChar = pos
                chapterNumber += 1
                pageNumber = 1
                newChapter = False
            
            # remaining characters to next page
            carryOver = page[lastChar:pageSize]
		
	# read next kb
        page = f.read(pageSize)

    return pagesDictionary

def main(args):
    opts,args = getopt.getopt(args, 'hf:o:')
    usage = "Usage: jsonify -h -f <input text> -o <output file>"

    for opt, arg in opts:
        if opt == "-h":
            print(usage)
            sys.exit(2)
        elif opt == "-f":
            if not os.path.isfile(arg):
                print("Error, missing input file")
                print(usage)
                sys.exit(2)
            else:
                fileIn = open(arg)
        elif opt == "-o":
            fileOut = arg

    # read first kb of characters
    page = fileIn.read(pageSize)   
    pagesDictionary = jsonify(fileIn, page)

#finish
    f = open(fileOut, "w+")
    f.write(json.dumps(pagesDictionary))
    f.close()
    print("Complete! -> %s" % fileOut)

if __name__ == "__main__":
    main(sys.argv[1:])

