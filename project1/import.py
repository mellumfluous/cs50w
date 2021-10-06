# Run *once* to create the necessary tables and insert the books into them.
# If the table(s) is/are already created, comment out the corresponding CREATE TABLE line(s)

import csv
import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# https://pypi.org/project/python-dotenv/
# how to load the .env file
# load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)

    # This is how I created the tables. You can comment them out if this isn't helpful. There's one more
    #  reate statement at the bottom
    db.execute("CREATE TABLE books ( bookID SERIAL PRIMARY KEY, isbn VARCHAR UNIQUE, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL);")
    db.execute("CREATE TABLE users ( userID SERIAL PRIMARY KEY, username VARCHAR UNIQUE, password VARCHAR NOT NULL);")

    # first row is the header, use the following line to skip it
    next(reader, None)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn": isbn, "title": title, "author": author, "year": year })
        print(f"added isbn: {isbn}, title: {title}, author: {author}, year: {year}")
    db.execute("CREATE TABLE reviews ( review VARCHAR, rating, INT, userID int REFERENCES users(userID), bookID int REFERENCES books(bookID), PRIMARY KEY (userID, bookID));")
    db.commit()

if __name__ == "__main__":
    main()