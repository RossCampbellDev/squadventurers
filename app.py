#!/usr/bin/python3.6
from flask import Flask, render_template, send_from_directory, request, session, redirect
# from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import flask_login
import json
import os
from os import path
import random
import datetime
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
# app.config['SERVER_NAME'] = "squadventurers.co.uk"

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

def updateChapters():
    contents.clear() 
    if session.get('book') is None:
        session['book'] = 1

    # get the navigation pane data
    count = 0
    fname = "snakes/chapters_" + str(session.get('book')) + ".txt"
    
    if path.exists(fname):
        with open(fname) as f:
            count = 0
            fl = f.readlines()
            for l in fl:
                if len(l) > 0:
                    count = count + 1
                    contents.append("%d.  %s" % (count, capitalise(l)))
    else:
        return home()

def setupNavInfo():
    if session.get('book') is None:
        session['book'] = 1

    # get the navigation pane data
    count = 0
    fname = "snakes/chapters_" + str(session.get('book')) + ".txt"
    if path.exists(fname):
        with open(fname) as f:
            count = 0
            fl = f.readlines()
            for l in fl:
                if len(l) > 0:
                    count = count + 1
                    contents.append("%d.  %s" % (count, capitalise(l)))
    else:
        return home()

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
            if l.split(",")[0].replace("\n","") == IP:
                unique = False


    if unique:
        f = open("visitors","a+")
        count = count + 1
        f.write(IP + "," + str(datetime.datetime.now()) + "\n")
        f.close()
    # print("total unique visitors:\t%d" % count)

# logout
@app.route("/logout")
def logout():
    session['logged-in'] = False
    session.pop('logged-in')
    session['free'] = False
    session.pop('free')
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
        cursor.execute("SELECT PassPhrase,PersonID FROM People WHERE lower(UserName)=%s", (user.lower(),))
        
        results = cursor.fetchall()
        cursor.close()
        
        paidup = 0
        if len(results) > 0:
            if b.check_password_hash(results[0][0].encode('utf-8'), userpass):
                session['logged-in'] = True
                session['user'] = user
                session['pid'] = results[0][1]
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=1)
            else:
                session['logged-in'] = False

    return home()


def checkPurchase(personID, bookID):
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM WhoBought WHERE PersonID=%s AND BookID=%s", (personID, bookID,))
    rc = cursor.fetchall()
    if rc == 0:
        return False;
    else:
        return True;

@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    if len(contents) == 0:
        setupNavInfo()
    
    # check login and then render template
    if session.get('logged-in'):
        bookData = {}   # contains book ID and flag to show if purchased
        bookNames = {}  # contains book ID and corresponding book name

        # grab list of all books, and see if they've been purchased or not
        # create dictionary of book names too
        cursor = db.connection.cursor()
        cursor.execute("SELECT BookID,BookName FROM Books ORDER BY BookID ASC")
        rows = cursor.fetchall()
        for row in rows:
            print(str(row[0]) + " " + str(session.get('pid')))
            rc = cursor.execute("SELECT PersonID FROM WhoBought WHERE BookID=%s AND PersonID=%s",(row[0], session.get('pid'),))
            bookNames[row[0]] = row[1]
            # if there's a rowcount > 0 then we know the user purchased it
            if rc > 0:
                bookData[row[0]] = 1
            else:
                bookData[row[0]] = 0

        return render_template('index.html', bData=bookData, bNames=bookNames)

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
        #paidup = request.form['paidup']
        #if paidup == "on":
        #    paidup = 1
        #else:
        #    paidup = 0

        # hash the pw
        b = Bcrypt()
        userpass = b.generate_password_hash(userpass)

        cursor = db.connection.cursor()

        # check for duplicate
        rc = cursor.execute("SELECT * FROM People WHERE lower(UserName)=%s OR (FirstName=%s AND LastName=%s)", (user.lower(),fname,lname,))
        if rc > 0:
            return render_template("register.html", problem="exists")

        # get max id
        pid = 1
        rc = cursor.execute("SELECT MAX(PersonID) FROM People")
        if rc > 0:
            rows = cursor.fetchall()
            pid = rows[0][0] + 1
            if pid == None:
                pid = 1

        # if no duplicate, insert
        #cursor.execute("INSERT INTO People (FirstName,LastName,UserName,Email,PassPhrase,PaidUp) VALUES (%s, %s, %s, %s, %s, %s)", (fname,lname,user,email,userpass,paidup,))
        cursor.execute("INSERT INTO People (PersonID,FirstName,LastName,UserName,Email,PassPhrase) VALUES (%s, %s, %s, %s, %s, %s)", (pid,fname,lname,user,email,userpass,))

        db.connection.commit()
        return render_template("login.html", newName=user)

    # default action, and for before post
    return render_template("register.html")


@app.route("/buy", defaults={"bookNum":None})
@app.route("/buy/<bookNum>" )
@app.route("/buy/<bookNum>", methods=['POST'])
def buy(bookNum):
    # check login first otherwise they can't buy
    if session.get('logged-in') == None:
        return home()

    if bookNum == None:
        return home()

    # if they have submitted the form
    # - check payment
    # - update WhoBought table
    # - success message or redirect
    # else
    # - return buy page
    cursor = db.connection.cursor()
    rc = cursor.execute("SELECT BookName FROM Books WHERE BookID=%s",(bookNum,))
    if rc > 0:
        rows = cursor.fetchall()
        bookName = rows[0][0]
    else:
        # invalid booknum
        return home()

    return render_template("buy.html", bk=bookNum, bkName=bookName)


@app.route("/<pageNum>", defaults={"chapterNum":"None", "bookNum":"None"})
@app.route("/<pageNum>/<chapterNum>", defaults={"bookNum":"None"})
@app.route("/<pageNum>/<chapterNum>/<bookNum>")
def read(pageNum, chapterNum, bookNum):
    freeRead = False
    cursor = db.connection.cursor()
    pid = 0 # default user id, for checking purchase

    if not session.get('logged-in'):
        if not session.get('free'): # if not on free read, then return home 
            return home()
    else:
        rc = cursor.execute("SELECT PersonID FROM People WHERE UserName='" + session.get('user') + "'")
        if rc > 0:
            rows = cursor.fetchall()
            pid = rows[0][0]

    # if it's a free read then don't allow past chapter 3
    #if session.get('free') and not checkPurchase(pid, bookNum):
    if not checkPurchase(pid, bookNum):
        freeRead = True
        try:
            if int(pageNum) > 29 or int(chapterNum) > 3:
                return buy(1)
        except ValueError:
            print("wtf value error")

    # default the values if new session
    if bookNum == "None":
        if session.get('book') is None:
            bookNum=1
            session['book'] = int(bookNum) # should always be 1 or a selected value
        else:
            bookNum=session.get('book')
            session['book'] = int(bookNum) # should always be 1 or a selected value
    else:
        if session.get('book') is not None:
            if bookNum != session.get('book'):
                session['book'] = int(bookNum)
                session['page'] = 1
                session['chapter'] = 1


    # check to see if they have paid for the book
    if int(bookNum) > 1:
        rc = cursor.execute("SELECT * FROM WhoBought WHERE PersonID=" + str(pid) + " AND BookID=" + str(bookNum))
        if rc == 0:
            return buy(bookNum)

    updateChapters()

    if session.get('page') is None:
        session['page'] = 1

    if session.get('chapter') is None:
        session['chapter'] = 1

    # if they are logged in and there IS session data for the page number,
        # go to that page if they've defaulted to page 1
    if session.get('page') is not None and pageNum is not None:
        if session.get('page') > 2 and int(pageNum) == 1: # >2 so that we can go back to page 1
            return read(session.get('page'),0,bookNum)# session.get('chapter')) # pass 0 chapter to just go to page directly

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
    fname = "books/augmented/" + str(bookNum) + ".txt"
    if path.exists(fname):
        with open(fname) as f:
            j = json.load(f)
    else:
        return home()

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
                return render_template("read.html", thisPage=thisPage, contents=contents, characters=characters, places=places, free=freeRead, bNum=bookNum)


    # look for the searched-for page within the JSON data
    for page in j:
        if page["absoluteCount"] == pageNum:
            thisPage["absoluteCount"] = int(page["absoluteCount"])
            thisPage["pageText"] = page["pageText"]
            thisPage["chapterNum"] = int(page["chapterNum"])
            return render_template("read.html", thisPage=thisPage, contents=contents, characters=characters, places=places, free=freeRead, bNum=bookNum)

    # if we're not looking for a specific page or chapter, go to the index
    session['page'] = 1
    session['chapter'] = 1
    return render_template("theend.html")
    return render_template("index.html")


# show the biography page for a character/place/object
# default to something else if none given
@app.route("/bio", defaults={"nameIn":"None"})
@app.route("/bio/<nameIn>")
def bio(nameIn):
    if not session.get('logged-in') and not session.get('free') :
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

@app.route('/freeRead')
def freeRead():
    session['free'] = True
    return redirect("/1", code=302)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon2.ico',mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    # if hosting on pythonanywhere, comment the app.run line
    app.run(debug=True, host="0.0.0.0", port=8080)
