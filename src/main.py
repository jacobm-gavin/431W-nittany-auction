import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv
import random

app = Flask(__name__)
app.secret_key = "secret_key"
load_dotenv()

# SQL GETTERS

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

        # Determine role from other tables
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
    
def get_listing(seller_email, listing_ID):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM auction_listings WHERE seller_email = %s AND Listing_ID = %s", (seller_email, listing_ID,))
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


def get_bids(seller_email, listing_ID):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM bids WHERE seller_email = %s AND listing_ID = %s", (seller_email, listing_ID,))
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

def get_credit_cards(owner_email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM credit_cards WHERE owner_email = %s ORDER BY credit_card_num", (owner_email,))

        cards = cursor.fetchall()

        cursor.close()
        conn.close()

        return cards if cards else []

    except mysql.connector.Error as err:
        print("Database error:", err)
        return []

def get_specific_card(owner_email, credit_card_num):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM credit_cards WHERE owner_email = %s AND credit_card_num = %s LIMIT 1", (owner_email, credit_card_num))
        card = cursor.fetchone()
        cursor.close()
        conn.close()

        return card

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    
def get_notifications(bidder_email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM notifications WHERE bidder_email = %s", (bidder_email,))

        notifications = cursor.fetchall()

        cursor.close()
        conn.close()

        return notifications

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

def insert_transaction(transaction_ID, seller_email, listing_ID, buyer_email, date, payment):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor()

        now = datetime.now()
        date = f"{now.month}/{now.day}/{str(now.year)[2:]}"

        cursor.execute("INSERT INTO transactions (transaction_ID, seller_email, listing_ID, buyer_email, date, payment) VALUES (%s, %s, %s, %s, %s, %s)", (transaction_ID, seller_email, listing_ID, buyer_email, date, payment))

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except mysql.connector.Error as err:
        print("Database error:", err)
        return False

#Used for check when paying to ensure transaction doesnt exist
def transaction_exists(seller_email, listing_ID):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM transactions WHERE seller_email = %s AND listing_ID = %s LIMIT 1", (seller_email, listing_ID))

        exists = cursor.fetchone() is not None

        cursor.close()
        conn.close()

        return exists

    except mysql.connector.Error as err:
        print("Database error:", err)
        return False

def add_to_seller_balance(seller_email, amount):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor()

        cursor.execute("UPDATE sellers SET balance = balance + %s WHERE email = %s", (amount, seller_email))

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except mysql.connector.Error as err:
        print("Database error:", err)
        return False

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


def get_full_profile(email):
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root",
            password=os.getenv("DB_PASSWORD"), database="nittanyauction"
        )
        cursor = conn.cursor(dictionary=True)

        query = """SELECT u.email,
                       b.first_name, \
                       b.last_name, \
                       b.age, \
                       b.major,
                       s.bank_routing_number, \
                       s.bank_account_number,
                       v.business_name, \
                       v.customer_service_phone_number,
                       a.street_num, \
                       a.street_name, \
                       a.zipcode,
                       z.city, \
                       z.state
                FROM users u
                         LEFT JOIN bidders b ON u.email = b.email
                         LEFT JOIN sellers s ON u.email = s.email
                         LEFT JOIN local_vendors v ON u.email = v.email
                         LEFT JOIN address a ON (b.home_address_id = a.address_ID
                    OR v.business_address_id = a.address_ID)
                         LEFT JOIN zipcode_info z ON a.zipcode = z.zipcode
                WHERE u.email = %s \
                """
        cursor.execute(query, (email,))
        profile = cursor.fetchone()

        if not profile:
            return {'email': email, 'cards': []}

        cursor.execute("SELECT * FROM credit_cards WHERE owner_email = %s ORDER BY credit_card_num", (email,))
        card_data = cursor.fetchall()
        profile['cards'] = card_data if card_data else []

        cursor.close()
        conn.close()
        return profile
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return {'email': email, 'cards': []}
    
def get_ratings(seller_email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM rating WHERE seller_email = %s", (seller_email,))
        ratings = cursor.fetchall()

        if ratings is None:
            cursor.close()
            conn.close()
            return None

        cursor.close()
        conn.close()

        return ratings

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

# SQL INSERTS

def insert_new_user(form_data):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )
        cursor = conn.cursor()

        # Retrieve user info from register.html
        email = form_data.get("email")
        password = hashlib.sha256(str(form_data.get("password")).encode()).hexdigest()
        role = form_data.get("role")
        zip_code = form_data.get("zipcode")
        city = form_data.get("city")
        state = form_data.get("state")

        # Add a new zipcode for a new city, and ignore if zipcode for city/state already exists
        cursor.execute("""INSERT IGNORE INTO Zipcode_Info (zipcode, city, state) VALUES (%s, %s, %s)""", (zip_code, city, state))

        # Insert address w/ random addr id
        import random
        address_id = random.randint(10000, 99999)  # Increased range for uniqueness
        cursor.execute("""INSERT INTO Address (address_ID, zipcode, street_num, street_name) VALUES (%s, %s, %s, %s)""", (address_id, zip_code, form_data.get("street_num"), form_data.get("street_name")))

        # Insert user
        cursor.execute("INSERT INTO Users (email, password) VALUES (%s, %s)", (email, password))

        # Insert to specific role
        if role == "buyer":
            # Bidder
            cursor.execute("""INSERT INTO Bidders (email, first_name, last_name, age, home_address_id, major) VALUES (%s, %s, %s, %s, %s, %s)""", (email, form_data.get("first_name"), form_data.get("last_name"), form_data.get("age"), address_id, form_data.get("major")))

        elif role == "seller":
            # Student Seller
            cursor.execute("""INSERT INTO Bidders (email, first_name, last_name, age, home_address_id, major) VALUES (%s, %s, %s, %s, %s, %s)""", (email, form_data.get("first_name"), form_data.get("last_name"), form_data.get("age"), address_id, form_data.get("major")))

            cursor.execute("""INSERT INTO Sellers (email, bank_routing_number, bank_account_number, balance) VALUES (%s, %s, %s, 0.0)""", (email, form_data.get("routing"), form_data.get("account")))

        elif role == "vendor":
            # Local Vendor
            cursor.execute("""INSERT INTO Sellers (email, bank_routing_number, bank_account_number, balance) VALUES (%s, %s, %s, 0.0)""", (email, form_data.get("routing"), form_data.get("account")))

            cursor.execute("""INSERT INTO Local_Vendors (Email, Business_Name, Business_Address_ID, Customer_Service_Phone_Number) VALUES (%s, %s, %s, %s)""", (email, form_data.get("business_name"), address_id, form_data.get("phone")))

        conn.commit()
        return True
    except mysql.connector.Error as err:
        print("Database error:", err)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def insert_listing(seller_email, listing_ID, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("INSERT INTO auction_listings VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (seller_email, listing_ID, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids, 1))

        conn.commit()
        
        cursor.close()
        conn.close()
        print("SUCCESSFULLY INSERTED LISTING")
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    
def insert_listing_audit(seller_email, listing_ID, remaining_bids, removal_reason):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("INSERT INTO listing_audit VALUES (%s, %s, %s, %s)", (seller_email, listing_ID, remaining_bids, removal_reason))

        conn.commit()
        
        cursor.close()
        conn.close()
        print("SUCCESSFULLY INSERTED LISTING AUDIT")
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    
def insert_bid(seller_email, listing_ID, bidder_email, bid_price):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT MAX(bid_ID) AS max_bid_id FROM bids")
        result = cursor.fetchone()
        next_bid_id = 1 if result["max_bid_id"] is None else result["max_bid_id"] + 1

        cursor.execute("INSERT INTO bids (bid_ID, seller_email, listing_ID, bidder_email, bid_price) VALUES (%s, %s, %s, %s, %s)", (next_bid_id, seller_email, listing_ID, bidder_email, bid_price,))

        conn.commit()
        
        cursor.close()
        conn.close()
        print("SUCCESSFULLY INSERTED BID")
        return True
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return False

def insert_notification(seller_email, listing_ID, bidder_email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("INSERT INTO notifications VALUES (%s, %s, %s)", (seller_email, listing_ID, bidder_email,))

        conn.commit()
        
        cursor.close()
        conn.close()
        print("SUCCESSFULLY INSERTED NOTFICATION")
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

# SQL UPDATES

def update_listing(seller_email, listing_ID, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("UPDATE auction_listings SET category = %s, auction_title = %s, product_name = %s, product_description = %s, quantity = %s, reserve_price = %s, max_bids = %s, status = %s WHERE seller_email = %s AND listing_ID = %s", (category, auction_title, product_name, product_description, quantity, reserve_price, max_bids, 1, seller_email, listing_ID,))

        conn.commit()
        
        cursor.close()
        conn.close()
        print("SUCCESSFULLY UPDATED LISTING")
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    
# Makes a listing inactive
def deactivate_listing(seller_email, listing_ID):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("UPDATE auction_listings SET status = 0 WHERE seller_email = %s AND listing_ID = %s", (seller_email, listing_ID))

        conn.commit()
        
        cursor.close()
        conn.close()
        print("SUCCESSFULLY DEACTIVATED LISTING")
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    
# Makes a listing sold (status = 2)
def sell_listing(seller_email, listing_ID):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("UPDATE auction_listings SET status = 2 WHERE seller_email = %s AND listing_ID = %s", (seller_email, listing_ID))

        conn.commit()
        
        cursor.close()
        conn.close()
        print("SUCCESSFULLY SOLD LISTING")
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

# SQL DELETES

def delete_notifications(bidder_email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )

        cursor = conn.cursor(dictionary=True)

        cursor.execute("DELETE FROM notifications WHERE bidder_email = %s", (bidder_email,))

        conn.commit()
        
        cursor.close()
        conn.close()
        print("SUCCESSFULLY DELETED NOTFICATIONS")
    
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

# HELPER FUNCTIONS

#ensures buyer completed the purchase
def get_transaction_for_buyer_listing(seller_email, listing_ID, buyer_email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM transactions WHERE seller_email = %s AND listing_ID = %s AND buyer_email = %s LIMIT 1", (seller_email, listing_ID, buyer_email))

        tran = cursor.fetchone()
        cursor.close()
        conn.close()
        return tran

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

#check to see if buyer already rated seller
def get_existing_rating(bidder_email, seller_email):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM rating WHERE bidder_email = %s AND seller_email = %s LIMIT 1",(bidder_email, seller_email))

        existing = cursor.fetchone()
        cursor.close()
        conn.close()
        return existing

    except mysql.connector.Error as err:
        print("Database error:", err)
        return None

#insert rating into DB
def insert_rating(bidder_email, seller_email, rating_value, rating_desc):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="nittanyauction"
        )
        cursor = conn.cursor()

        now = datetime.now()
        date = f"{now.month}/{now.day}/{str(now.year)[2:]}"

        cursor.execute(
            "INSERT INTO rating (bidder_email, seller_email, date, rating, rating_desc) VALUES (%s, %s, %s, %s, %s)",
            (bidder_email, seller_email, date, rating_value, rating_desc)
        )

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as err:
        print("Database error:", err)
        return False
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
    notifications = get_notifications(email)

    for notif in notifications:
        listing = get_listing(notif["seller_email"], notif["listing_ID"])
        notif["auction_title"] = listing["auction_title"]

    if notifications:
        delete_notifications(email)

    name = get_first_name(email)
    if name == None:
        name = get_business_name(email)

    return render_template("buyer.html",
                           user=session["user"],
                           role=session["role"],
                           name=name,
                           listings=listings,
                           categories=categories,
                           category=category,
                           notifications=notifications)

@app.route("/buyer/<string:category>")
def buyer_category(category):
    if "user" not in session or session.get("role") not in ["buyer", "seller"]:
        return redirect(url_for("login"))
    
    listings = get_auction_listings(category)
    categories = parse_categories(get_categories())
    category = category
    email = session["user"]
    name = get_first_name(email)
    if name == None:
        name = get_business_name(email)

    return render_template("buyer.html", user=session["user"], role=session["role"], name=name, listings=listings, categories=categories, category=category)

@app.route("/payment/<string:seller_email>/<int:listing_ID>", methods=["GET", "POST"])
def payment(seller_email, listing_ID):
    if "user" not in session:
        return redirect(url_for("login"))

    buyer_email = session["user"]

    if session.get("seller_type") == "vendor":
        flash("Only buyers can complete payments.")
        return redirect(url_for("login"))
    #ensure listing is loaded
    listing = get_listing(seller_email, listing_ID)
    if listing is None:
        flash("Listing not found.")
        return redirect(url_for("buyer"))

    bids = get_bids(seller_email, listing_ID)
    latestbid = get_latest_bid(bids)

    #check to see if listing has bids
    if latestbid is None:
        flash("No winning bid is present for this listing.")
        return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

    #ensure listing eached max bids before declaring winner
    if len(bids) < listing["max_bids"]:
        flash("This auction is not over yet.")
        return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

    #ensure reserve price met
    if latestbid["bid_price"] < listing["reserve_price"]:
        flash("Reserve price not met.")
        return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

    #ensure bidder that is paying was the one who won the auction
    if buyer_email != latestbid["bidder_email"]:
        flash("You are not authorized to pay for this listing.")
        return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

    if transaction_exists(seller_email, listing_ID):
        flash("Already paid for this listing.")
        return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

    saved_cards = get_credit_cards(buyer_email)
    amount_due = latestbid["bid_price"]

    if request.method == "POST":
        selected_card_num = request.form.get("selected_card_num", "").strip()

        #inputted credit card
        credit_card_num = request.form.get("credit_card_num", "").strip()
        card_type = request.form.get("card_type", "").strip()
        expire_month = request.form.get("expire_month", "").strip()
        expire_year = request.form.get("expire_year", "").strip()
        security_code = request.form.get("security_code", "").strip()

        #option to pay with card already on file
        if selected_card_num:
            chosen_card = get_specific_card(buyer_email, selected_card_num)

            if chosen_card is None:
                flash("Selected saved card was not found.")
                return render_template("payment.html",user=buyer_email,role=session["role"],listing=listing,latestbid=latestbid,saved_cards=saved_cards,amount_due=amount_due)
        else:
            #ensure inputted card has all fields
            if not credit_card_num or not card_type or not expire_month or not expire_year or not security_code:
                flash("Please either choose a saved card or enter a complete new card.")
                return render_template("payment.html",user=buyer_email,role=session["role"],listing=listing,latestbid=latestbid,saved_cards=saved_cards,amount_due=amount_due)

            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password=os.getenv("DB_PASSWORD"),
                    database="nittanyauction"
                )

                cursor = conn.cursor()

                cursor.execute("""
                    INSERT IGNORE INTO credit_cards
                    (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    credit_card_num,
                    card_type,
                    expire_month,
                    expire_year,
                    security_code,
                    buyer_email
                ))

                conn.commit()
                cursor.close()
                conn.close()

            except mysql.connector.Error as err:
                print("Database error:", err)
                flash("Could not save payment information.")
                return render_template("payment.html",user=buyer_email,role=session["role"],listing=listing,latestbid=latestbid,saved_cards=saved_cards,amount_due=amount_due)

        transaction_ID = random.randint(100000, 999999)
        date = "2026-04-21"

        done = insert_transaction(
            transaction_ID,
            seller_email,
            listing_ID,
            buyer_email,
            date,
            amount_due
        )

        if not done:
            flash("Payment failed. Please try again.")
            return render_template("payment.html",user=buyer_email,role=session["role"],listing=listing,latestbid=latestbid,saved_cards=saved_cards,amount_due=amount_due)

        add_to_seller_balance(seller_email, amount_due)
        sell_listing(seller_email, listing_ID)

        flash("Payment successful.")
        return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

    return render_template("payment.html",user=buyer_email,role=session["role"],listing=listing,latestbid=latestbid,saved_cards=saved_cards,amount_due=amount_due)


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

@app.route("/auction_listing/<string:seller_email>/<int:listing_ID>", methods=["GET", "POST"])
def auction_listing(seller_email, listing_ID):
    if "user" not in session:
        return redirect(url_for("login"))
    
    listing = get_listing(seller_email, listing_ID)
    if listing is None:
        flash("Listing not found.")
        return redirect(url_for("buyer"))

    bids = get_bids(seller_email, listing_ID)
    numbids = len(bids)
    rating_data = get_ratings(seller_email)
    ratings = []
    #debug statement for divide by zero error
    if rating_data:
        for rating in rating_data:
            ratings.append(float(rating["rating"]))
    if len(ratings) > 0:
        avg_rating = round((sum(ratings) / len(ratings)), 1)
    else:
        avg_rating = 0

    # find latest bid just by maximum bid_price
    latestbid = get_latest_bid(bids)

    #variables for rating restrictions
    can_rate = False
    already_rated = False

    if "user" in session and (session.get("role") == "buyer" or session.get("seller_type") != "vendor"):
        buyer_email = session["user"]
        transaction = get_transaction_for_buyer_listing(seller_email, listing_ID, buyer_email)
        existing_rating = get_existing_rating(buyer_email, seller_email)

        if transaction is not None:
            can_rate = True

        if existing_rating is not None:
            already_rated = True

    if request.method == "POST":
        action = request.form.get("action", "").strip()

        if action == "submit_rating":
            buyer_email = session["user"]
            rating_raw = request.form.get("rating_value", "").strip()

            transaction = get_transaction_for_buyer_listing(seller_email, listing_ID, buyer_email)

            #ensure user won auction before rating
            if transaction is None:
                flash("You can only rate a seller after purchasing this item.")
                return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

            existing_rating = get_existing_rating(buyer_email, seller_email)

            #ensure user hasnt already rated
            if existing_rating is not None:
                flash("You have already rated this seller.")
                return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

            try:
                #whole number check for inputted rating
                rating_value = int(rating_raw)
            except ValueError:
                flash("Rating must be a whole number from 1 to 5.")
                return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))
            #rating domain restriction
            if rating_value < 1 or rating_value > 5:
                flash("Rating must be between 1 and 5.")
                return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

            if rating_value == 5 or rating_value == 4:
                rating_desc = "Awesome"
            elif rating_value == 3:
                rating_desc = "Not Bad"
            else:
                rating_desc = "Bad"
            done = insert_rating(buyer_email, seller_email, rating_value, rating_desc)

            if not done:
                flash("Rating could not be submitted.")
                return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

            flash("Seller rating submitted successfully.")
            return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

        if action == "place_bid":
            new_bid_raw = request.form.get("new_bid", "").strip()

            if not new_bid_raw:
                flash("Please enter a price.")
                return render_template("auction_listing.html",user=session["user"],role=session["role"],seller_type=session.get("seller_type", "none"),listing=listing,bids=bids,numbids=numbids,latestbid=latestbid,avg_rating=avg_rating, can_rate=can_rate, already_rated=already_rated )

            try:
                new_bid = int(new_bid_raw)
            except ValueError:
                #valid inputted number check for bid
                flash("Bid must be a valid number.")
                return render_template("auction_listing.html",user=session["user"],role=session["role"],
                seller_type=session.get("seller_type", "none"),listing=listing,bids=bids,numbids=numbids,latestbid=latestbid,avg_rating=avg_rating, can_rate=can_rate, already_rated=already_rated)

            if session["user"] == seller_email:
                flash("You cannot bid on your own listing.")
                return render_template("auction_listing.html",user=session["user"],role=session["role"],seller_type=session.get("seller_type", "none"),listing=listing,bids=bids,numbids=numbids,latestbid=latestbid,avg_rating=avg_rating, can_rate = can_rate, already_rated=already_rated)

            if listing["status"] != 1:
                flash("This auction is no longer active.")
                return render_template("auction_listing.html",user=session["user"],role=session["role"],seller_type=session.get("seller_type", "none"),listing=listing,bids=bids,numbids=numbids,latestbid=latestbid,avg_rating=avg_rating, can_rate = can_rate, already_rated=already_rated)

            if latestbid is not None:
                if session["user"] == latestbid["bidder_email"]:
                    flash("You cannot place consecutive bids.")
                    return render_template("auction_listing.html",user=session["user"],role=session["role"],seller_type=session.get("seller_type", "none"),listing=listing,bids=bids,numbids=numbids,latestbid=latestbid,avg_rating=avg_rating, can_rate = can_rate, already_rated=already_rated)

                #restriction that new bid must be higher
                if new_bid <= latestbid["bid_price"]:
                    flash("Bid must be higher than current bid.")
                    return render_template(
                        "auction_listing.html",
                        user=session["user"],
                        role=session["role"],
                        seller_type=session.get("seller_type", "none"),
                        listing=listing,
                        bids=bids,
                        numbids=numbids,
                        latestbid=latestbid,
                        avg_rating=avg_rating)

            success = insert_bid(seller_email, listing_ID, session["user"], new_bid)

            if not success:
                flash("Bid could not be placed. Check terminal for the database error.")
                return render_template(
                    "auction_listing.html",
                    user=session["user"],
                    role=session["role"],
                    seller_type=session.get("seller_type", "none"),
                    listing=listing,
                    bids=bids,
                    numbids=numbids,
                    latestbid=latestbid,
                    avg_rating=avg_rating)

        bids = get_bids(seller_email, listing_ID)
        numbids = len(bids)
        latestbid = get_latest_bid(bids)

        if numbids >= listing["max_bids"]:
            # users_to_notify = []
            for bid in bids:
                if bid["bidder_email"] != latestbid["bidder_email"]:
                    insert_notification(seller_email, listing_ID, bid["bidder_email"])

            if latestbid is not None and latestbid["bid_price"] >= listing["reserve_price"]:
                if session["user"] == latestbid["bidder_email"]:
                    flash("You won the auction. Please complete payment.")
                    return redirect(url_for("payment", seller_email=seller_email, listing_ID=listing_ID))
                else:
                    flash("Auction has ended. You did not win this item.")
                    return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))
            else:
                deactivate_listing(seller_email, listing_ID)
                flash("Reserve price was not met. Auction closed.")
                return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

            flash("Bid placed successfully.")
            return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

        flash("Bid placed successfully.")
        return redirect(url_for("auction_listing", seller_email=seller_email, listing_ID=listing_ID))

    return render_template("auction_listing.html", user=session["user"], role=session["role"], seller_type=session["seller_type"], listing=listing, bids=bids, numbids=numbids, latestbid=latestbid, avg_rating=avg_rating, can_rate = can_rate, already_rated=already_rated)

@app.route("/sell_item", methods=["GET", "POST"])
def sell_item():
    if "user" not in session or session.get("role") != "seller":
        return redirect(url_for("login"))
    
    categories = parse_categories(get_categories())
    # going to have to convert categories into just a flat, non-hierarchical array of all categories to render in page
    all_categories = set()

    for parent, children in categories.items():
        all_categories.add(parent)
        all_categories.update(children)

    if 'Root' in all_categories:
        all_categories.remove('Root')

    flat_category_list = sorted(list(all_categories))

    if request.method == "POST":
        auction_title = request.form.get("auction_title", "").strip()
        product_name = request.form.get("product_name", "").strip()
        product_description = request.form.get("product_description", "").strip()
        reserve_price = request.form.get("reserve_price", "").strip()
        quantity = request.form.get("quantity", "").strip()
        max_bids = request.form.get("max_bids", "").strip()
        category = request.form.get("category", "").strip()

        if not auction_title or not product_name or not product_description or not reserve_price or not quantity or not max_bids or category == "Select a category":
            flash("Please complete all fields.")
            return render_template("sell_item.html", user=session["user"], categories=flat_category_list, seller_type=session["seller_type"])
        
        # NOTE!!!
        # listing_IDs for auction_listings seem to be randomly generated numbers in the given dataset
        # in order to insert new listings while making sure listing_IDs are unique
        # we will keep schema as is and just increment ID numbers from the highest existing ID for each seller
        
        # E.g.
        # if a seller has 2 listings with IDs of 4 and 281
        # making a new listing will have an ID of 282
        seller_listings = get_seller_listings(session["user"])
        listing_IDs = []
        for listing in seller_listings:
            listing_IDs.append(listing["listing_ID"])

        if listing_IDs:
            new_listing_ID = max(listing_IDs) + 1 # creating new listing_ID
        else:
            new_listing_ID = 1
        insert_listing(session["user"], new_listing_ID, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids)

        return redirect(url_for("seller"))
    
    return render_template("sell_item.html", user=session["user"], categories=flat_category_list, seller_type=session["seller_type"])

@app.route("/edit_item/<string:seller_email>/<int:listing_ID>", methods=["GET", "POST"])
def edit_item(seller_email, listing_ID):
    if "user" not in session and session["role"] != "seller":
        return redirect(url_for("login"))
    
    listing = get_listing(seller_email, listing_ID)
    categories = parse_categories(get_categories())
    all_categories = set()

    for parent, children in categories.items():
        all_categories.add(parent)
        all_categories.update(children)

    if 'Root' in all_categories:
        all_categories.remove('Root')

    flat_category_list = sorted(list(all_categories))

    if request.method == "POST":
        auction_title = request.form.get("auction_title", "").strip()
        product_name = request.form.get("product_name", "").strip()
        product_description = request.form.get("product_description", "").strip()
        reserve_price = request.form.get("reserve_price", "").strip()
        quantity = request.form.get("quantity", "").strip()
        max_bids = request.form.get("max_bids", "").strip()
        category = request.form.get("category", "").strip()

        if auction_title is "" or product_name is "" or product_description is "" or reserve_price is "" or quantity is "" or max_bids is "" or category is "":
            flash("Please fill in all fields.")
            return render_template("edit_item.html", user=session["user"], listing=listing, categories=flat_category_list, seller_type=session["seller_type"])
        
        update_listing(seller_email, listing_ID, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids)
        listing = get_listing(seller_email, listing_ID)

        flash("Item successfully updated!")
        return redirect(f"/auction_listing/{seller_email}/{listing_ID}")
    
    return render_template("edit_item.html", user=session["user"], listing=listing, categories=flat_category_list, seller_type=session["seller_type"])

@app.route("/remove_item/<string:seller_email>/<int:listing_ID>", methods=["GET", "POST"])
def remove_item(seller_email, listing_ID):
    if "user" not in session and session["role"] != "seller":
        return redirect(url_for("login"))

    if request.method == "POST":
        removal_reason = request.form.get("removal_reason", "").strip()

        if removal_reason is "":
            flash("Please provide a reason.")
            return render_template("remove_item.html")
        
        listing = get_listing(seller_email, listing_ID)
        bids = get_bids(seller_email, listing_ID)
        numbids = len(bids)
        remaining_bids = listing["max_bids"] - numbids

        deactivate_listing(seller_email, listing_ID)
        insert_listing_audit(seller_email, listing_ID, remaining_bids, removal_reason)

        flash("Item successfully removed!")
        return render_template("remove_item.html")
    
    return render_template("remove_item.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Attempt to insert the user into the DB
        if insert_new_user(request.form):
            # auto-login start
            email = request.form.get("email").strip()
            role = request.form.get("role")

            # Set session variables just like the /login route does
            session["user"] = email
            session["role"] = "buyer" if role == "buyer" else "seller"
            session["seller_type"] = "none"

            # Handle the specific vendor/student seller distinction
            if role == "vendor":
                session["seller_type"] = "vendor"
                session["role"] = "seller"
            elif role == "seller":
                session["seller_type"] = "student"
                session["role"] = "seller"

            flash("Registration successful! Welcome to NittanyAuction.")

            # Redirect to the appropriate dashboard immediately
            if session["role"] == "buyer":
                return redirect(url_for("buyer"))
            else:
                return redirect(url_for("seller"))
            # auto login logic end

        flash("Registration failed. Email might already exist.")
    return render_template("register.html")


@app.route("/my_account", methods=["GET", "POST"])
def my_account():
    if "user" not in session:
        return redirect(url_for("login"))

    email = session["user"].strip().lower()
    role = session.get("role")

    if request.method == "POST":
        action = request.form.get("action")

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password=os.getenv("DB_PASSWORD"),
                database="nittanyauction"
            )
            cursor = conn.cursor(dictionary=True)

            if action == "update_profile":
                # update Password
                new_pw = request.form.get("password", "").strip()
                if new_pw:
                    hashed = hashlib.sha256(new_pw.encode()).hexdigest()
                    cursor.execute("UPDATE Users SET password = %s WHERE email = %s", (hashed, email))

                # Address and Zipcode
                zip_c = request.form.get("zipcode", "").strip()
                if zip_c:
                    # Ensure Zip exists first (Parent table)
                    cursor.execute("""
                                   INSERT
                                   IGNORE INTO Zipcode_Info (zipcode, city, state) 
                        VALUES (%s, %s, %s) """, (zip_c, request.form.get("city"), request.form.get("state")))

                    # Update Address (Child table)
                    cursor.execute("""
                                   UPDATE Address
                                   SET zipcode = %s, street_num  = %s, street_name = %s WHERE address_ID = (SELECT home_address_id FROM Bidders WHERE email = %s)""", (zip_c, request.form.get("street_num"), request.form.get("street_name"), email))

                # Update Personal Info
                cursor.execute("""
                               UPDATE Bidders
                               SET first_name = %s,
                                   last_name  = %s
                               WHERE email = %s """, (request.form.get("first_name"), request.form.get("last_name"), email))

                flash("Profile information updated successfully!")

            elif action == "update_payment":
                if role == "buyer":
                    #get credit card info
                    credit_card_num = request.form.get("credit_card_num", "").strip()
                    card_type = request.form.get("card_type", "").strip()
                    expire_month = request.form.get("expire_month", "").strip()
                    expire_year = request.form.get("expire_year", "").strip()
                    security_code = request.form.get("security_code", "").strip()

                    if not credit_card_num or not card_type or not expire_month or not expire_year or not security_code:
                        flash("Please fill in all credit card fields.")
                    else:
                        cursor.execute("REPLACE INTO Credit_Cards(credit_card_num, card_type, expire_month, expire_year, security_code, owner_email) VALUES (%s,%s,%s,%s,%s,%s)", (credit_card_num,card_type,expire_month,expire_year,security_code,email))
                        flash("Payment card updated!")
                else:
                    # banking for Sellers/Vendors
                    bank_routing_number = request.form.get("bank_routing_number", "").strip()
                    bank_account_number = request.form.get("bank_account_number", "").strip()
                    cursor.execute("UPDATE Sellers SET bank_routing_number = %s,bank_account_number = %s WHERE email = %s", (bank_routing_number, bank_account_number, email))
                    flash("Banking information updated!")

            elif action == "delete_card":
                if role == "buyer":
                    delete_card_num = request.form.get("delete_card_num", "").strip()

                    if not delete_card_num:
                        flash("No card was selected for deletion.")
                    else:
                        cursor.execute("DELETE FROM Credit_Cards WHERE credit_card_num = %s AND owner_email = %s", (delete_card_num, email))
                        flash("Card deleted successfully.")

            # Auto fill description for requesting email change
            elif action == "request_email_change":
                new_email_req = request.form.get("new_email_request")
                request_id = random.randint(10000, 99999)
                cursor.execute("""
                               INSERT INTO Requests (request_id, sender_email, helpdesk_staff_email, request_type,
                                                     request_desc, request_status)
                               VALUES (%s, %s, 'helpdeskteam@lsu.edu', 'ChangeID', %s, 0)""", (request_id, email, f"Request to change email to: {new_email_req}"))
                flash("Email change request submitted to HelpDesk.")

            conn.commit()
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            flash("An error occurred while updating your information.")

    current_data = get_full_profile(email)

    # DEBUG print
    print(f"Template Data: {current_data}")

    return render_template("my_account.html", user_info=current_data)


@app.route("/search")
def search():
    query_param = request.args.get('q', '').strip()
    min_p = request.args.get('min_p')
    max_p = request.args.get('max_p')

    try:
        conn = mysql.connector.connect(
            host="localhost", user="root",
            password=os.getenv("DB_PASSWORD"), database="nittanyauction"
        )
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT category_name, parent_category FROM categories")
        rows = cursor.fetchall()
        categories_dict = {}
        for row in rows:
            parent = row['parent_category'] or "Root"
            if parent not in categories_dict:
                categories_dict[parent] = []
            categories_dict[parent].append(row['category_name'])

        # Statement to search specific listings
        search_sql = """
                     SELECT * \
                     FROM auction_listings
                     WHERE (product_name LIKE %s OR product_description LIKE %s
                         OR category LIKE %s OR auction_title LIKE %s OR seller_email LIKE %s)
                       AND status = 1 \
                     """
        search_val = f"%{query_param}%"
        # Use user value to search in name, description, category, title, or seller
        params = [search_val, search_val, search_val, search_val, search_val]

        # Set min and max prices if given
        if min_p:
            search_sql += " AND reserve_price >= %s"
            params.append(min_p)
        if max_p:
            search_sql += " AND reserve_price <= %s"
            params.append(max_p)

        cursor.execute(search_sql, tuple(params))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        email = session["user"]
        name = get_first_name(email)
        if name == None:
            name = get_business_name(email)

        # Render with filtered listings
        return render_template("buyer.html",
                               listings=results,
                               categories=categories_dict,
                               name=name,
                               user=session.get('user'),
                               role=session.get('role'),
                               category=f"Search Results: {query_param}")

    except Exception as e:
        print(f"Search Error: {e}")
        return redirect(url_for('buyer'))

if __name__ == "__main__":
    app.run(debug=True)