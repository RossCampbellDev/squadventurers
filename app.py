#!/usr/bin/python3.6
from flask import Flask, render_template, send_from_directory, request, session
# from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import flask_login
import json
import os
import random
from datetime import timedelta
#import pymysql
#from flask_mysqldb import MySQl

#db = pymysql.connect("localhost", "gandalf", "300LivesOfMen!", "BookDatabase")
app = Flask(__name__) #create app variable and make instance of Flask class
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Squadventurers.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)

app.secret_key = "wtf kind of secret key is this"
app.config['SESSION_TYPE'] = 'filesystem'

with open("config") as f:
    app.config['MYSQL_HOST'] = f.readline().strip('\n')#'localhost'
    app.config['MYSQL_USER'] = f.readline().strip('\n')#'gandalf'
    app.config['MYSQL_PASSWORD'] = f.readline().strip('\n')#'300LivesOfMen!'
    app.config['MYSQL_DB'] = f.readline().strip('\n')#'BookDatabase'

db = MySQL(app)

# set up login test vars
user = ""
userpass = ""
paidup = False

def capitalise(s):
    return ' '.join(w[0].upper() + w[1:].lower() for w in s.split(' '))

# set up the three nav arrays
contents = []
characters = []
places = []

def setupNavInfo():
    # get the navigation pane data
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


setupNavInfo()

def checkIP():
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

# logout
@app.route("/logout")
def logout():
    session['logged-in'] = False
    app.secret_key = os.urandom(12)
    return home()


# behaviour for the index page and reading chapters
@app.route("/", methods=['POST'])
@app.route("/index", methods=['POST'])
@app.route("/home", methods=['POST'])
def checkLogin():
    if session.get('logged-in'):
        return home()

    # check if user logged in
    if request.method == "POST":
        user = request.form['user']
        userpass = request.form['userpass'].encode('utf-8')
        b = Bcrypt()
        # userpass = b.generate_password_hash(userpass)
        cursor = db.connection.cursor()
        cursor.execute("SELECT PaidUp,PassPhrase FROM People WHERE lower(UserName)=%s", (user.lower(),))
        
        results = cursor.fetchall()
        cursor.close()
        
        paidup = 0
        if len(results) > 0:
            if b.check_password_hash(results[0][1].encode('utf-8'), userpass):
                paidup = results[0][0]
                session['logged-in'] = True
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=1)
            else:
                session['logged-in'] = False

    return home()


@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    # check login and then render template
    if session.get('logged-in'):
        return render_template('index.html')

    return render_template('login.html', newName="")


@app.route("/createUser")
@app.route("/createUser", methods=['POST'])
def createUser():
    if request.method == "POST":
        fname = request.form['fname']
        lname = request.form['lname']
        user = request.form['user']
        email = request.form['email']
        userpass = request.form['userpass'].encode('utf-8')
        paidup = request.form['paidup']
        if paidup == "on":
            paidup = 1
        else:
            paidup = 0

        # hash the pw
        b = Bcrypt()
        userpass = b.generate_password_hash(userpass)

        cursor = db.connection.cursor()

        # check for duplicate
        cursor.execute("SELECT * FROM People WHERE lower(UserName)=%s OR (FirstName=%s AND LastName=%s)", (user.lower(),fname,lname,))
        if cursor.rowcount > 0:
            return render_template("register.html", problem="exists")

        # if no duplicate, insert
        cursor.execute("INSERT INTO People (FirstName,LastName,UserName,Email,PassPhrase,PaidUp) VALUES (%s, %s, %s, %s, %s, %s)", (fname,lname,user,email,userpass,paidup,))

        db.connection.commit()
        return render_template("login.html", newName=user)

    # default action, and for before post
    return render_template("register.html")

@app.route("/<pageNum>", defaults={"chapterNum":"None"})
@app.route("/<pageNum>/<chapterNum>")
def read(pageNum, chapterNum):
    if not session.get('logged-in'):
        return home()
    else:
        # default the values if new session
        if session.get('page') is None:
            session['page'] = 1

        if session.get('chapter') is None:
            session['chapter'] = 1

        # if they are logged in and there IS session data for the page number,
        # go to that page if they've defaulted to page 1
        if session.get('page') is not None and pageNum is not None:
            if session.get('page') > 2 and int(pageNum) == 1: # >2 so that we can go back to page 1
                return read(session.get('page'),0)# session.get('chapter')) # pass 0 chapter to just go to page directly

        # if they navigated to a chapter and stopped
        # if session.get('chapter') is not None and session.get('page') is None:
            # return read(0, session.get('chapter'))

        # update the session to show what page they're on
        if pageNum != "None":
            session['page'] = int(pageNum)

        if chapterNum != "None":
            session['chapter'] = int(chapterNum)

    # set up the page (book text and chapter etc
    thisPage={}
    
    if pageNum == "None":
        pageNum = 1

    # load the pre-generated JSON data into a JSON dictionary
    with open("chapters/AllPages") as f:
        j = json.load(f)

    pageNum = int(pageNum)

    # look for unique visitors - almost certainly gonna be ppl on page 1!
    if pageNum == 1:
        checkIP()

    # looking for a specific chapter, so return the right page as soon as we find it
    if chapterNum != "None":
        chapterNum = int(chapterNum)
        for page in j:
            if int(page["chapterNum"]) == chapterNum:
                session['page'] = int(page["absoluteCount"])
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
    if not session.get('logged-in'):
        return home()

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
    # if hosting on pythonanywhere, comment the app.run line
    app.run(debug=True, host="0.0.0.0", port=8080)
