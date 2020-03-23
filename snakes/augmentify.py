#!/usr/bin/env python2.7
import sys
import getopt
import os

# add the trimmings to the file using the given dictionary
# or remove them in the case of plaintextify
def augmentifyThis(fileIn, dictionary, plaintextify):
    replacementDict = {}

    # iterate over the dictionary file to grab all pairs of words and their replacements
    # strip newline chars
    for line in dictionary:
        lineSplit = line.split(",")
        replacementDict[lineSplit[0]] = lineSplit[1].rstrip()

    # iterate over each dictionary pair and replace all instances in the input file
    f = fileIn.read()
    fileIn.close()
    newdata = f

    for k,v in replacementDict.items():
        if plaintextify:
            newdata = newdata.replace(v,k)
        else:
            newdata = newdata.replace(k,v)

    if not plaintextify:
        return "<br />".join(newdata.splitlines())
    else: 
        return newdata.replace("<br />","")

def markupThis(textIn, chapters):
    returnText = textIn
    n = 1
    for line in chapters:
        returnText = returnText.replace("CHAPTER " + str(n), "<div class='title-main'>CHAPTER " + str(n) + "</div>")
        returnText = returnText.replace(line, "<div class='title-sub'>" + line + "</div>")
        n += 1

    return returnText


def main(args):
    opts,args = getopt.getopt(args, 'hrf:d:o:c:')

    usage = "usage: augmentify -h -f <text file in> -d <dictionary file in> [-o <file out>] -c <chapters file>\nUse -r flag to plaintextify (reverse process)"
    fileIn=""
    dictionary=""
    fileOut=""
    chapters=""
    plaintextify = False

    for opt, arg in opts:
        if opt == "-h":
            print(usage)
            print("Dictionary file must be in key-value pairs.\n<originalChars,replacementChars>")
            sys.exit(2)
        if opt == "-r":
            plaintextify = True
        elif opt == "-f":
            if not os.path.isfile(arg):
                print("Error, missing input plaintext file")
                print(usage)
                sys.exit(2)
            else:
                fileIn = open(arg)
        elif opt == "-d":
            if not os.path.isfile(arg):
                print("Error, missing input dictionary file")
                print(usage)
                sys.exit(2)
            else:
                dictionary = open(arg)
        elif opt == "-o":
            fileOut = arg
        elif opt == "-c":
            chapters = open(arg)

    # passed all checks, go!
    result = augmentifyThis(fileIn, dictionary, plaintextify)
    result = markupThis(result, chapters)

    if fileOut == "":
        print(result)
    else:
        #if os.path.isfile(fileOut):
        f = open(fileOut, "w+")
        print("output to file: %s" % fileOut)
        #else:
            #f = open("augmentified_text", "w+")
            #print("output to file: augmentified_text")
    
        f.write(result)
        f.close()



if __name__ == "__main__":
    main(sys.argv[1:])

