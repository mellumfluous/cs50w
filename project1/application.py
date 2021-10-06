# make sure to do `pip install requests`

import os
import json
import requests
from flask import Flask, render_template, request, url_for, redirect, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["POST", "GET"])
def index():
    # If a user is signed in, bring to the "main" search page
    if "username" in session:
        return render_template("main.html", user=session["username"])
    # Else have them sign in
    return render_template("index.html")

# Intermediate fn between signup and login so url looks prettier
# By the time I was finishing up this project, I realized I hadn't used this as much
# as I thought I would, but it still made some parts look prettier (it says "home") so I kept it
@app.route("/home", methods=["POST", "GET"])
def home():
    if "username" in session:
        return render_template("main.html", user=session["username"])
    return redirect(url_for("index"))

@app.route("/signed_up", methods=["POST", "GET"])
def signup():
    # If someone "claims" to have signed up when they hadn't, bring them home
    if request.method == "GET":
        return redirect(url_for("home"))
    
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # If the username's taken, give an error message and have them try again.
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount != 0:
        return render_template("index.html", signup_msg = "Sorry, it looks like that username is taken. Please pick another username.")

    # If time permits, figure out how to salt/hash password and make it not show up as clear text
    # It's about time to start the next project so I'll leave this for next time, but I wish I got time to work on it
    # Username should be unique, so insert the new user to db

    # from werkzeug.security import generate_password_hash
# generate_password_hash(password)
# https://werkzeug.palletsprojects.com/en/1.0.x/utils/#werkzeug.security.generate_password_hash

    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
    db.commit()

    # Set session info and go to the "main" search page
    # I didn't end up using the userid very much 
    session["username"] = username
    session["userid"] =  db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()["userid"]
    return redirect(url_for("home"))


@app.route("/logged_in", methods=["POST", "GET" ])
def login():

    # Get credentials and see if it exists
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 0:
        return render_template("index.html", login_msg = "Sorry, your credentials are not in our database.")

    # https://stackoverflow.com/questions/20743806/sqlalchemy-execute-return-resultproxy-as-tuple-not-dict
    # https://docs.sqlalchemy.org/en/13/core/connections.html#sqlalchemy.engine.ResultProxy
    # more info on resultproxy
    user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
    session["username"] = user["username"]
    session["userid"] = user["userid"]
    return redirect(url_for("home"))

# Clear everything in the session and go to the signup page
@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return render_template("index.html")

# A webpage so the user can see their reviews
@app.route("/reviews", methods=["POST", "GET" ])
def reviews():

    # If a user is logged in, then whether they get this page through POST or GET, they can view their reviews
    if "username" in session:
        review_results = db.execute("SELECT * FROM reviews JOIN books ON reviews.bookid = books.bookid WHERE reviews.userid = :userid",{"userid": session["userid"]})
        return render_template("reviews.html", 
            user=session.get("username"), review_results = review_results)
    return redirect(url_for("home"))

# used following link for horizontal scrolling
# https://stackoverflow.com/questions/9707807/how-to-force-horizontal-scrolling-in-an-html-list-using-css
@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "GET" and "username" not in session:
        return redirect(url_for("home"))

    # When the user refreshes the page, the same results will populate the page.
    # I wanted to clear the previous contents when the page is refreshed, but I guess that'll be for
    # next time

    # Horrible name for what it is -the "title" that tells the user that the following list of
    # books is the authors, titles, isbns, that matched the search
    author = "authors that matched your query"
    title = "book titles that matched your query"
    isbn = "isbns that matched your query"

    # If you query the db for something LIKE xxx then you need wildcards % before and after
    # so the db knows there may be text before or after and to search for that
    query = request.form.get("query", "")
    query = "%" + query + "%"

    # better names
    author_results = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:query)", {"query": query})
    title_results = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(:query)", {"query": query})
    isbn_results = db.execute("SELECT * FROM books WHERE LOWER(isbn) LIKE :query", {"query": query})

    # also better names
    author_message = "Sorry, there were no authors with that name"
    title_message = "Sorry, there were no titles matching your query"
    isbn_message = "Sorry, there were no isbns matching your query"

    return render_template("main.html", user = session["username"],
        author = author, title = title, isbn = isbn,
        author_results = author_results, title_results = title_results, isbn_results = isbn_results,
        author_message = author_message, title_message = title_message, isbn_message = isbn_message)

# display info about book
@app.route("/search/<string:isbn>", methods=["POST", "GET"])
def search_result(isbn):
    # This is getting repetitive
    if request.method == "GET" and "username" not in session:
        return redirect(url_for("home"))

    book = get_book_from(isbn)

    # No rowcount means we didn't find anything so the book doesn't exist in the db
    if request.method == "GET":
        if book.rowcount == 0:
            return render_template("error.html", message=f"Sorry, we don't have a book with isbn: {isbn} in our database")

    # I looked over the books.csv isbns and they all seem to be unique, so I'm hardcoding this fetchone statement
    book = book.fetchone()
    author = book["author"]
    title = book["title"]
    year = book["year"]

    # goodreads_info() gets the goodreads json object given isbn
    goodreads = goodreads_info(isbn)

    # join the users and reviews table to get the reviews of the users on this website
    review_results = db.execute("SELECT rating, username, review FROM reviews join users ON reviews.userid = users.userid WHERE bookid = :bookid",{"bookid": book["bookid"]})

    user = session["username"]
    return render_template("book_page.html", user=session["username"],
        goodreads = goodreads, review_results = review_results, book = book)

@app.route("/search/<string:isbn>/review_submitted", methods=["POST", "GET"])
def review_submitted(isbn):
    if request.method == "GET" and "username" not in session:
        return redirect(url_for("index"))

    user = session["username"]
    book = get_book_from(isbn).fetchone()
    goodreads = goodreads_info(isbn)
    rating = request.form.get("rating", "")
    review = request.form.get("review", "")
    userid = session["userid"]
    bookid = book["bookid"]

    # Rowcount returns a number. In python 0 is false and 1 is true. If the number of rows we get back from this query
    # is nonzero then the review exists and we update it. Else it's zero and we insert it
    review_exists = db.execute("SELECT * FROM reviews WHERE userid = :userid AND bookid = :bookid", {
        "userid": session["userid"], "bookid": book.bookid}).rowcount

    if review_exists:
        db.execute("UPDATE reviews SET review = :review, rating = :rating WHERE userid = :userid AND bookid = :bookid", {
            "review": review, "rating": rating, "userid": userid, "bookid": bookid})
        message = "your review was updated!"
    else: 
        db.execute("INSERT INTO reviews (review, rating, userid, bookid) VALUES (:review, :rating, :userid, :bookid)",
            {"review": review, "rating": rating, "userid": userid, "bookid": bookid})
        message = "added your review!"
    db.commit()

    review_results = db.execute("SELECT rating, username, review FROM reviews join users ON reviews.userid = users.userid WHERE bookid = :bookid",{"bookid": book["bookid"]})

    return render_template("book_page.html",
        goodreads = goodreads, user = user, message = message, book = book, review_results = review_results)

# woohoo, one page where I don't do the user check
@app.route("/api/<string:isbn>", methods=["POST", "GET"])
def api(isbn):

    # I'm not sure how'd they get here through post, but just in case ...
    if request.method == "POST":
        return render_template("error.html", message = "Sorry, we couldn't find that page. If you'd like to get the api page, it's 'api/<isbn>'. Else, try visiting our home page!")
    book = get_book_from(isbn).fetchone()


    # https://stackoverflow.com/questions/19317777/sql-queries-on-bookid
    # https://www.w3resource.com/sql/creating-views/create-view-with-count-sum-avg.php
    # I wish I knew how to make this shorter

    book = get_book_from(isbn).fetchone()
    average = 0
    count = 0

    reviews_info = db.execute("SELECT AVG(rating) , COUNT(review)  FROM reviews JOIN books ON reviews.bookid = books.bookid WHERE books.isbn = :isbn GROUP BY books.title, books.author, books.year",
        {"isbn": isbn}).fetchone()

    if reviews_info is not None:
        count = reviews_info["count"]
        average = float(reviews_info["avg"])

    api_obj = {
        "title": book["title"],
        "author": book["author"],
        "year": book["year"],
        "isbn": isbn,
        "review_count": count,
        "average_score": average,
    }
    json_obj = json.dumps(api_obj)
    return json_obj

def get_isbn_string(isbn):
    # when I inserted the rows from books.csv to heroku, the isbns where len < 10 had 0s prepended to it
    # add the necessary 0s and then query the db
    append = ""
    if len(isbn) < 10:
        append += "0"*(10-len(isbn))
    # Don't have to add % to either side because we're looking for an exact match
    return append+isbn

# Honestly, this is the best name I've come up with ... ever
def get_book_from(isbn):
    return db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": get_isbn_string(isbn)})

# It's just one line, but it's a bit long so I made this function
def goodreads_info(isbn):
    return requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("KEY"), "isbns": isbn}).json()["books"][0]


