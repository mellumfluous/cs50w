# Project 1

Web Programming with Python and JavaScript

application.py - Has ample comments to show what I'm trying to do, links to what helped me, what I wanted to do if I had time, etc. Might be a bit fluffy

books.csv - Given for the project. I didn't change anything

import.py - I used this to both create my users, reviews, and books tables and to insert the 5,000 books.csv rows to books table on heroku. I deleted my db a few times so it was handy having everything here to recreate it for me

static/style.css - The css file

templates/layout.html - Basic layout of the page for someone not signed in

templates/logged_in_layout.html - layout for when someone's logged in. Will say their username, has some buttons on the top right to go to the home search page, to see their reviews, and to log out.

templates/api.html - Extends layout.html and that's about it

templates/book_page.html - Information about the book title, author, year, goodreads average rating, and number of ratings. There's a section for the user to rate and review the book. The bottom is a row of some of the reviews other users on the website have left on the book.

templates/error.html - The 404 error page. Will include a message about the error when the user gets it

templates/index.html - Both the login and sign up page for users. They're also more or less redirected here if they try to reach other pages without signing in

templates/main.html - The page that logged in users first see (the serach page). This page will populate with search results when the user searches for them.

templates/reviews.html - A page that shows all the reviews that the current user has made on this website.

Things I wish I implemented/had done differently

- everything password related - hashing/salting the password, "hiding" the password when the user types it in, making sure the password is decently strong

- better url names

- figure out a way to shorten application.py so there's less duplicate code

- figure out how to get the picture of a book and some goodreads reviews using the goodreads api so the page has a little more oomph to it than just text

- figure out a better way to go about "GET" requests for pages when a user isn't logged in. 

Other notes: 
Like many others, I had trouble setting the database_url so I installed dotenv (I also added it to the requirements.txt file in case). However, somewhere along the way, I realized that I didn't have the `load_env()` line in my application.py that I had in my `import.py` and that flask was running just fine without it. I'm not sure if installing dotenv made a difference, but everything works and I don't want to break it. Just wanted to put that out there in case there was confusion about it.