#!/usr/bin/python3.6

def read(pageNum, chapterNum, bookNum, db):
    freeRead = True     # assume free is true -> show buy button
    cursor = db.connection.cursor()
    pid = 0 # default user id, for checking purchase

    if not session.get('logged-in'):
        if not session.get('free'): # if not on free read, then return home 
            return home()
    else:
        rc = cursor.execute("SELECT PersonID FROM People WHERE UserName='" + session.get('user') + "'")
        if rc:
            rows = cursor.fetchall()
            pid = rows[0][0]


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

    # if it's a free read then don't allow past chapter 3
    # if session.get('free') and not checkPurchase(pid, bookNum):
    print("p: %s, b: %s" % (pid, bookNum))
    if checkPurchase(pid, bookNum) == False:
        try:
            if int(pageNum) > 29 or int(chapterNum) > 3:
                return buy(bookNum)
        except ValueError:
            print("wtf value error")
    else:
        freeRead = False

    # check to see if they have paid for the book
    if int(bookNum) > 1:
        rc = cursor.execute("SELECT * FROM WhoBought WHERE PersonID=" + str(pid) + " AND BookID=" + str(bookNum))
        if not rc or rc==0:
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
            return read(session.get('page'),0,bookNum,db)# session.get('chapter')) # pass 0 chapter to just go to page directly

    # if they navigated to a chapter and stopped
    # if session.get('chapter') is not None and session.get('page') is None:
        # return read(0, session.get('chapter'))

    # update the session to show what page they're on
    if pageNum != "None":
        session['page'] = int(pageNum)

    if chapterNum != "None":
        session['chapter'] = int(chapterNum)

    # set up the page (book text and chapter etc)
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

                if pid and chapterNum and page["absoluteCount"]:
                    UpdateCurrentPage(pid,bookNum,page["absoluteCount"])

                return render_template("read.html", thisPage=thisPage, contents=contents, characters=characters, places=places, free=freeRead, bNum=bookNum)


    # look for the searched-for page within the JSON data
    for page in j:
        if page["absoluteCount"] == pageNum:
            thisPage["absoluteCount"] = int(page["absoluteCount"])
            thisPage["pageText"] = page["pageText"]
            thisPage["chapterNum"] = int(page["chapterNum"])

            if pid and chapterNum and page["absoluteCount"]:
                UpdateCurrentPage(pid,bookNum,page["absoluteCount"])

            return render_template("read.html", thisPage=thisPage, contents=contents, characters=characters, places=places, free=freeRead, bNum=bookNum)

    # if we're not looking for a specific page or chapter, go to the index
    session['page'] = 1
    session['chapter'] = 1
    return render_template("theend.html")
    return render_template("index.html")

