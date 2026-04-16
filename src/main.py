import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import mysql.connector
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "secret_key"
load_dotenv()

# SQL FUNCTIONS

def get_user(email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        # users table lookup
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            conn.close()
            return None

        # determine role from other tables
        role = None

        cursor.execute("SELECT * FROM bidders WHERE email = %s", (email,))
        if cursor.fetchone():
            role = "buyer"

        cursor.execute("SELECT * FROM sellers WHERE email = %s", (email,))
        if cursor.fetchone():
            role = "seller"

        cursor.execute("SELECT * FROM helpdesk WHERE email = %s", (email,))
        if cursor.fetchone():
            role = "helpdesk"

        user["role"] = role

        cursor.close()
        conn.close()
        print("USER FETCHED FROM USERS TABLE:", user)

        return user


    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    
def get_auction_listings(category):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        if (category == None):
            cursor.execute("SELECT * FROM auction_listings WHERE status = 1") # updated to only show active items
        else:
            cursor.execute("SELECT * FROM auction_listings WHERE status = 1 AND category = %s", (category,))
        listings = cursor.fetchall()

        if listings is None:
            cursor.close()
            conn.close()
            return None
        
        cursor.close()
        conn.close()
        # print("AUCTION LISTINGS FETCHED:", listings)

        return listings
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    
def get_seller_listings(email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM auction_listings WHERE seller_email = %s", (email,))
        listings = cursor.fetchall()

        if listings is None:
            cursor.close()
            conn.close()
            return None
        
        cursor.close()
        conn.close()
        # print("AUCTION LISTINGS FETCHED:", listings)

        return listings
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    
def get_listing(listing_ID):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM auction_listings WHERE Listing_ID = %s", (listing_ID,))
        listing = cursor.fetchone()

        if listing is None:
            cursor.close()
            conn.close()
            return None
        
        cursor.close()
        conn.close()
        # print("AUCTION LISTING FETCHED:", listing)

        return listing
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

def get_categories():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()

        if categories is None:
            cursor.close()
            conn.close()
            return None
        
        cursor.close()
        conn.close()
        # print("CATEGORIES FETCHED:", categories)

        return categories
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None


def get_bids(listing_ID):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM bids WHERE Listing_ID = %s", (listing_ID,))
        bids = cursor.fetchall()

        if bids is None:
            cursor.close()
            conn.close()
            return None

        cursor.close()
        conn.close()
        # print("BIDS FETCHED:", bids)

        return bids

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

def get_first_name(email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT first_name FROM bidders WHERE email = %s", (email,))
        first_name = cursor.fetchone()

        if first_name is None:
            cursor.close()
            conn.close()
            return None

        first_name = first_name["first_name"]

        cursor.close()
        conn.close()

        return first_name

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

def get_business_name(email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT business_name FROM local_vendors WHERE email = %s", (email,))
        business_name = cursor.fetchone()

        if business_name is None:
            cursor.close()
            conn.close()
            return None

        business_name = business_name["business_name"]

        cursor.close()
        conn.close()

        return business_name

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

# HELPER FUNCTIONS

# Input - Retrieved bids on a listing from database
# Output - Latest bid on that listing
def get_latest_bid(bids):
    if bids:
        latestbid = bids[0]
        for bid in bids:
            if bid["bid_price"] > latestbid["bid_price"]:
                latestbid = bid
        return latestbid
    return None

# Input - Raw category data from the database
# Output - Hierarchal categories array for easier HTML rendering
def parse_categories(category_data):
    categories = {}
    for category in category_data:
        if category["parent_category"] not in categories:
            categories[category["parent_category"]] = []
            
        categories[category["parent_category"]].append(category["category_name"])
            
    # print("TEST", categories)
    return categories

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Please enter both email and password.")
            return render_template("login.html")

        hashed = hashlib.sha256(str(password).encode()).hexdigest()
        user = get_user(email)

        print("EMAIL ENTERED:", email)
        print("PASSWORD ENTERED:", password)
        print("HASHED ENTERED PASSWORD:", hashed)
        print("USER RETURNED:", user)
        if user is not None:
            print("STORED PASSWORD FROM DB:", user["password"])
            print("ROLE FOUND:", user.get("role"))

        if user is None:
            flash("Invalid email or password.")
            return render_template("login.html")

        if user["password"] != hashed:
            flash("Invalid email or password.")
            return render_template("login.html")

        if user["role"] is None:
            flash("No valid user role found.")
            return render_template("login.html")

        session["user"] = email
        session["role"] = user["role"]
        session["seller_type"] = "none"

        if user["role"] == "buyer":
            return redirect(url_for("buyer"))
        elif user["role"] == "seller":
            return redirect(url_for("seller"))
        elif user["role"] == "helpdesk":
            return redirect(url_for("helpdesk"))

        flash("Unknown role.")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/buyer")
def buyer():
    if "user" not in session and session["seller_type"] != "vendor":
        return redirect(url_for("login"))
    
    listings = get_auction_listings(None)
    categories = parse_categories(get_categories())
    category = None
    email = session["user"]
    name = get_first_name(email)
    if name == None:
        name = get_business_name(email)

    return render_template("buyer.html", user=session["user"], role=session["role"], name=name, listings=listings, categories=categories, category=category)

@app.route("/buyer/<string:category>")
def buyer_category(category):
    if "user" not in session and session["seller_type"] != "vendor":
        return redirect(url_for("login"))
    
    listings = get_auction_listings(category)
    categories = parse_categories(get_categories())
    category = category
    email = session["user"]
    name = get_first_name(email)
    if name == None:
        name = get_business_name(email)

    return render_template("buyer.html", user=session["user"], role=session["role"], name=name, listings=listings, categories=categories, category=category)


@app.route("/seller")
def seller():
    if "user" not in session or session.get("role") != "seller":
        return redirect(url_for("login"))
    
    email = session["user"]
    name = get_first_name(email)
    session["seller_type"] = "student"

    # in the dataset, all student sellers are also bidders
    # but the sellers that are local vendors are not in bidders table
    # this means we should keep track of who's a local vendor
    # because local vendors are not bidders, so they should not be able to browse
    if name == None:
        name = get_business_name(email)
        session["seller_type"] = "vendor"

    listings = get_seller_listings(email)

    # separate lists for each category of listing (active, inactive, sold)
    # just so it's easier on the rendering side
    active = []
    inactive = []
    sold = []

    for listing in listings:
        if listing["status"] == 0:
            inactive.append(listing)
        elif listing["status"] == 1:
            active.append(listing)
        elif listing["status"] == 2:
            sold.append(listing)

    # numA, numIA, and numS is just length of active (A), inactive (IA), and sold (S) arrays respectively
    return render_template("seller.html", user=session["user"], seller_type=session["seller_type"], name=name, active=active, inactive=inactive, sold=sold, numA=len(active), numIA=len(inactive), numS=len(sold))


@app.route("/helpdesk")
def helpdesk():
    if "user" not in session or session.get("role") != "helpdesk":
        return redirect(url_for("login"))
    return render_template("helpdesk.html", user=session["user"])


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))

@app.route("/auction_listing/<string:seller_email>/<int:listing_ID>")
def auction_listing(seller_email, listing_ID):
    if "user" not in session:
        return redirect(url_for("login"))
    
    listing = get_listing(listing_ID)
    bids = get_bids(listing_ID)
    numbids = len(bids)
    # print(session["user"])

    # find latest/current bid just by maximum bid_price
    latestbid = get_latest_bid(bids)
        
    return render_template("auction_listing.html", user=session["user"], role=session["role"], seller_type=session["seller_type"], listing=listing, bids=bids, numbids=numbids, latestbid=latestbid)

if __name__ == "__main__":
    app.run(debug=True)