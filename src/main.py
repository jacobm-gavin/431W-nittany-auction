import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import mysql.connector
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "secret_key"
load_dotenv()

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
    
def get_auction_listings():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM auction_listings WHERE status = 1") # updated to only show active items
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
    
# just a helper function once bids are retrieved
def get_latest_bid(bids):
    if bids:
        latestbid = bids[0]
        for bid in bids:
            if bid["bid_price"] > latestbid["bid_price"]:
                latestbid = bid
        return latestbid
    return None

# parses raw category data from SQL into the proper hierarchy
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
    if "user" not in session or session.get("role") != "buyer":
        return redirect(url_for("login"))
    
    listings = get_auction_listings()
    categories = parse_categories(get_categories())

    return render_template("buyer.html", user=session["user"], listings=listings, categories=categories)


@app.route("/seller")
def seller():
    if "user" not in session or session.get("role") != "seller":
        return redirect(url_for("login"))
    return render_template("seller.html", user=session["user"])


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

@app.route("/auction_listing/<int:listing_ID>") # slight error; primary key for listing items is actually seller + listingID, will just keep this for now but should probably update later
def auction_listing(listing_ID):
    if "user" not in session or session.get("role") != "buyer":
        return redirect(url_for("login"))
    
    listing = get_listing(listing_ID)
    bids = get_bids(listing_ID)
    numbids = len(bids)

    # find latest/current bid just by maximum bid_price
    latestbid = get_latest_bid(bids)
        
    return render_template("auction_listing.html", user=session["user"], listing=listing, bids=bids, numbids=numbids, latestbid=latestbid)

if __name__ == "__main__":
    app.run(debug=True)