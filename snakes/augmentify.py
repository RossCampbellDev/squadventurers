#!/usr/bin/env python2.7
import sys
import getopt
import os
import re
import io

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
    newdata = f.replace("  ","&nbsp;&nbsp;")
    newdata = newdata.replace("*","<p style=\\\"text-align:center;color:#000;\\\">*</p>")

    for k,v in replacementDict.items():
        mask = r'\b%s\b' % k

        new = v

        if plaintextify:
            # newdata = newdata.replace(v,k)
            newdata = re.sub(new,mask,newdata)
        else:
            # newdata = newdata.replace(k,v)
            newdata = re.sub(mask,new,newdata)

    if not plaintextify:
        return "<br />".join(newdata.splitlines())
    else: 
        return newdata.replace("<br />","")

def markupThis(textIn, chapters):
    textIn = textIn.replace("\ufeff","")
    ch = chapters.read().split('\n')
    ch = ch[:-1]
    # reverse the array so that chapter 1 does not overwrite chapter 10-19 etc
    n = 1 
    for line in ch:
        mask = (r'\b%s\b' % ("CHAPTER " + str(n)))
        new = "<div class='title-main'>CHAPTER " + str(n) + "</div>"
        # returnText = returnText.replace("CHAPTER " + str(n), "<div class='title-main'>CHAPTER " + str(n) + "</div>")
        textIn = re.sub(mask, new, textIn)
        textIn = textIn.replace(line, "<div class='title-sub'>" + line + "...</div>")
        n += 1

    return textIn


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
                #fileIn = open(arg)
                fileIn = io.open(arg, mode='r', encoding='utf-8')
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

