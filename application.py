import os

from datetime import datetime, date
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)


####################################################
# The comments with two "#" or "##" are all the wrong code lines that were used in the making of this projektand were later discarded


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///projekt.db")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Register

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Register user
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure that the confirm password input field is not empty
        # Ensuring the password is input correctly the sencond time
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Enter the same password again", 403)

        # Query database to check username and if unique, insert it
        rows = db.execute("SELECT username FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # If username exists, reject it
        if len(rows) != 1:
            db.execute("INSERT INTO users (username, hash)"
                       "VALUES(:username, :password)",
                       username=request.form.get("username"),
                       password = generate_password_hash(request.form.get("password")))

        else:
            return apology("Username already exists", 403)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



# Index
@app.route("/")
@login_required
def index():
    """show reservations"""

    # Deleting data from pin table in db which might have not yet been deleted from last time
    db.execute("DELETE FROM pin WHERE user_id = :id", id = session['user_id'])


    ## date_format = "%Y-%m-%d"
    ## a = datetime.strftime(date.today(), date_format)

    # Setting today's date
    a = date.today()

    ## b = datetime.strftime(date.fromisoformat('2020-01-01'), date_format)

    # Taking a random date to calculate number of days passed and store it in database
    b = date.fromisoformat('2020-01-01')

    delta = a - b


    ## db.execute("INSERT INTO date (date, user_id) VALUES (:date, :id)", date = delta.days, id = session['user_id'])
    ## date2 = db.execute("SELECT date FROM date WHERE user_id = :id", id = session['user_id'])

    # Deleting data from the timeslot of the user that is 7 days old. Since, there is no use of any old reservations.
    # After 3 days the data will be automatically deleted in order to keep the database size small
    days = db.execute("SELECT date FROM timeslot WHERE customer_id = :id", id = session['user_id'])
    for day in days:
        delta2 = delta.days - days[0]['date']
        if delta2 > 3:
            db.execute("DELETE FROM timeslot WHERE customer_id = :id", id = session['user_id'])


    rows2 = db.execute("SELECT date FROM timeslot WHERE customer_id = :id AND date = :date", id = session['user_id'], date = delta.days)

    if len(rows2) != 0:

        shops = db.execute("SELECT * FROM timeslot WHERE customer_id = :id AND date = :date", id = session['user_id'], date = delta.days)

        for shop in shops:

            seller = db.execute("SELECT * FROM sellers WHERE user_id = :id", id = shop['seller_id'])

            shop['address'] = seller[0]['address']
            shop['name'] = seller[0]['name']

        ## db.execute("DELETE FROM date WHERE user_id = :id", id = session['user_id'])


        return render_template("index.html", shops = shops)

    else:

        ## db.execute("DELETE FROM date WHERE user_id = :id", id = session['user_id'])

        return render_template("nobooking.html")

# Reserve a shop
@app.route("/reserve", methods=["GET", "POST"])
@login_required
def reserve():
    """Reserve a Store Time"""

    # Deleting data from pin table in db which might have not yet been deleted from last tab
    db.execute("DELETE FROM pin WHERE user_id = :id", id = session['user_id'])


    # User reached route via POST (as by submitting a form via POST)

    if request.method == "POST":

            if not request.form.get("pin"):

                return apology("Input the Pin Code/ Postal Code")

            else:

                reservepin = request.form.get("pin")

                db.execute("INSERT INTO pin (pin, user_id) VALUES (:pin, :id)", pin = reservepin, id = session['user_id'])

                return redirect ("/check")

    else:

        return render_template("reserve.html")


# Reserve a shop: Check
@app.route("/check")
@login_required
def check():
    """Check if a shop is registered for a particular PIN Code/ Postal Code"""


    pin = db.execute("SELECT * FROM pin WHERE user_id = :id", id = session['user_id'])
    rows6 = db.execute("SELECT name FROM sellers WHERE pin = :pin", pin = pin[0]["pin"])

    if len(rows6) == 0:
        return render_template("no_shop_on_this_pin.html")
    else:
        return redirect ("/reservepin")



# Reserve a shop: Reserve pin
@app.route("/reservepin", methods=["GET", "POST"])
@login_required
def reservepin():
    """Show Shops to Order from"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("store"):

            return apology("Select a Store", 403)

        elif not request.form.get("time"):

            return apology("Select time", 403)

        else:

            ## date_format = "%Y-%m-%d"
            ## a = datetime.strftime(date.today(), date_format)

            a = date.today()

            ## b = datetime.strftime(date.fromisoformat('2020-01-01'), date_format)

            b = date.fromisoformat('2020-01-01')

            delta = a - b


            db.execute("INSERT INTO timeslot (customer_id, seller_id, time, date) VALUES (:id, :seller_id, :time, :date)",
                        id = session['user_id'], seller_id = request.form.get("store"),
                        time = request.form.get("time"), date = delta.days)

            db.execute("DELETE FROM pin WHERE user_id = :id", id = session['user_id'])

            return redirect("/")

    if request.method == "GET":



        pin = db.execute("SELECT * FROM pin WHERE user_id = :id", id = session['user_id'])

        shops = db.execute("SELECT * FROM sellers WHERE pin = :pin", pin = pin[0]["pin"])

        return render_template("reservepin.html", shops = shops)

# Register your shop

@app.route("/registershop", methods=["GET","POST"])
@login_required
def registershop():
    """register a shop of an owner"""

    # Deleting data from pin table in db which might have not yet been deleted from last tab
    db.execute("DELETE FROM pin WHERE user_id = :id", id = session['user_id'])

    # User reached route via POST
    if request.method == "POST":

        if not request.form.get("name"):

            return apology("Enter the Name", 403)

        elif not request.form.get("address"):

            return apology("Enter the Address", 403)

        elif not request.form.get("pin"):

            return apology("Enter the PIN Code/ Postal Code", 403)

        else:

            pin = request.form.get("pin")

            db.execute("INSERT INTO sellers (address, user_id, pin, name) VALUES (:address, :id, :pin, :name)", address = request.form.get("address"), id = session['user_id'], pin = pin.upper(), name = request.form.get("name"))

            return redirect("/")

    if request.method == "GET":

        rows3 = db.execute("SELECT name FROM sellers WHERE user_id = :id", id = session['user_id'])

        if len(rows3) == 0:

            return render_template("registershop.html")

        else:

            return render_template("alreadyregistered.html")



# Shop Reservation

@app.route("/shop_reservation")
@login_required
def shop_reservation():
    """show shop reservations"""

    # Deleting data from pin table in db which might have not yet been deleted from last tab
    db.execute("DELETE FROM pin WHERE user_id = :id", id = session['user_id'])

    rows4 = db.execute("SELECT * FROM sellers WHERE user_id = :id", id = session['user_id'])

    if len(rows4) != 0:

        ## date_format = "%Y-%m-%d"
        ## a = datetime.strftime(date.today(), date_format)

        a = date.today()

        ## b = datetime.strftime(date.fromisoformat('2020-01-01'), date_format)

        b = date.fromisoformat('2020-01-01')

        delta = a - b

        ## db.execute("INSERT INTO date (date, user_id) VALUES (:date, :id)", date = delta.days, id = session['user_id'])
        ## date2 = db.execute("SELECT date FROM date WHERE user_id = :id", id = session['user_id'])

        rows2 = db.execute("SELECT date FROM timeslot WHERE seller_id = :id AND date = :date", id = session['user_id'], date = delta.days)

        if len(rows2) != 0:

            customers = db.execute("SELECT * FROM timeslot WHERE seller_id = :id AND date = :date", id = session['user_id'], date = delta.days)
            seller = db.execute("SELECT * FROM sellers WHERE user_id = :id", id = session['user_id'])

            ## db.execute("DELETE FROM date WHERE user_id = :id", id = session['user_id'])

            return render_template("sellerreservations.html", customers = customers, seller = seller)

        else:

            ## db.execute("DELETE FROM date WHERE user_id = :id", id = session['user_id'])

            return render_template("nobooking_shop.html")
    else:

        return render_template("yougotnoshop.html")



# All Registered Shops

@app.route("/shops")
@login_required
def shops():
    """Registeres shops on the site"""

    # Deleting data from pin table in db which might have not yet been deleted from last tab
    db.execute("DELETE FROM pin WHERE user_id = :id", id = session['user_id'])


    allshops = db.execute("SELECT * FROM sellers")
    return render_template("allshops.html", allshops = allshops)


# Search

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Pin code of store"""

    # Deleting data from pin table in db which might have not yet been deleted from last tab
    db.execute("DELETE FROM pin WHERE user_id = :id", id = session['user_id'])

    if request.method == "POST":

        if not request.form.get("pincode"):

            return apology("Enter a pin code/ postal code", 403)

        rows5 = db.execute("SELECT name FROM sellers WHERE pin = :pin", pin = request.form.get("pincode"))

        if len(rows5) == 0:

            return render_template("noshop.html")

        else:

            store = db.execute("SELECT * FROM sellers WHERE pin = :pin", pin = request.form.get("pincode"))
            return render_template("searched.html", store = store)

    else:

        return render_template("search.html")





def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
