#!/usr/bin/python3.6
import json
import os
import random
from flask import Flask, render_template, send_from_directory, request

app = Flask(__name__) #create app variable and make instance of Flask class
# app.config['SERVER_NAME'] = 'squadventurers.co.uk:80'



def capitalise(s):
    return ' '.join(w[0].upper() + w[1:].lower() for w in s.split(' '))

# set up the three nav arrays
contents = []
characters = []
places = []

def setupNavInfo():
    count = 0
    with open("snakes/chapters") as f:
        count = 0
        fl = f.readlines()
        for l in fl:
            if len(l) > 0:
                count = count + 1
                contents.append("%d.  %s" % (count, capitalise(l)))

    with open("snakes/characters") as f:
        count = 0
        fl = f.readlines()
        for l in fl:
            if len(l) > 0:
                count = count+ 1
                characters.append("%s" % l)

    with open("snakes/places") as f:
        count = 0
        fl = f.readlines()
        for l in fl:
            if len(l) > 0:
                count = count+ 1
                places.append("%s" % l)



# behaviour for the index page and reading chapters
@app.route("/",)
@app.route("/index")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/<pageNum>", defaults={"chapterNum":"None"})
@app.route("/<pageNum>/<chapterNum>")
#@app.route("/", defaults={"pageNum":"None"})
#@app.route("/index", defaults={"pageNum":"None"})
#@app.route("/home", defaults={"pageNum":"None"})
#@app.route("/<pageNum>")
def read(pageNum, chapterNum):
    # check for new unique visitor
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        IP = request.environ['REMOTE_ADDR']
    else:
        IP = request.environ['HTTP_X_FORWARDED_FOR'] #proxy

    unique = True # always assume new visitor
    count = 0
    with open("visitors") as f:
        fl = f.readlines()
        for l in fl:
            count = count + 1
            if l.replace("\n","") == IP:
                unique = False


    if unique:
        f = open("visitors","a+")
        count = count + 1
        f.write(IP + "\n")
        f.close()
    # print("total unique visitors:\t%d" % count)


    # set up the page (book text and chapter etc
    thisPage={}
    
    if pageNum == "None":
        pageNum = 1

    # load the pre-generated JSON data into a JSON dictionary
    with open("chapters/AllPages") as f:
        j = json.load(f)

    pageNum = int(pageNum)

    # looking for a specific chapter, so return the right page as soon as we find it
    if chapterNum != "None":
        chapterNum = int(chapterNum)
        for page in j:
            if int(page["chapterNum"]) == chapterNum:
                thisPage["absoluteCount"] = int(page["absoluteCount"])
                thisPage["pageText"] = page["pageText"]
                thisPage["chapterNum"] = int(page["chapterNum"])
                return render_template("read.html", thisPage=thisPage, contents=contents, characters=characters, places=places)


    # look for the searched-for page within the JSON data
    for page in j:
        if page["absoluteCount"] == pageNum:
            thisPage["absoluteCount"] = int(page["absoluteCount"])
            thisPage["pageText"] = page["pageText"]
            thisPage["chapterNum"] = int(page["chapterNum"])
            return render_template("read.html", thisPage=thisPage, contents=contents, characters=characters, places=places)

    # if we're not looking for a specific page or chapter, go to the index
    return render_template("index.html")


# show the biography page for a character/place/object
# default to something else if none given
@app.route("/bio", defaults={"nameIn":"None"})
@app.route("/bio/<nameIn>")
def bio(nameIn):
    bios=[]
    temp_bio={}

    if nameIn != "None":
        with open("characters", "r") as f:
            for line in f:
                (name,desc) = line.split(",")
                temp_bio["name"] = name
                temp_bio["description"] = desc.rstrip()
                bios.append(temp_bio.copy())
    
        for bio in bios:
            if bio["name"] == nameIn:
                if nameIn == "Pantaloons":
                    bio["name"] = "The Crusty Pantaloons"
                thisEntity={}
                thisEntity["name"] = bio["name"]
                fi = open("menagerie/" + nameIn, "r")
                thisEntity["description"] = fi.read()
                fi.close()

        # open the quotes file and get all quotes for this character, then pick a random one
        quotesList = []
        count = 0
        with open("Quotes", "r") as f:
            fl = f.readlines()

        for l in fl:
            line = l.split("%")
            if line[0] == nameIn:
                count = count + 1
                quotesList.append(line[1])

        if count > 0:
            thisQuote = quotesList[random.randint(0, count-1)]
        else:
            thisQuote = ""

        return render_template("bio.html", entity=thisEntity, quote=thisQuote)
    else:
        return "<content-title>Bio Page</content-title>"

    return ""

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico',mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    setupNavInfo()
    app.run(debug=True, host="0.0.0.0", port=8080)
