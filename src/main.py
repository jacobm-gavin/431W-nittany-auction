import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import mysql.connector
from dotenv import load_dotenv

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
        print("SUCCESSFULLY INSERTED")
    
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
        print("SUCCESSFULLY UPDATED")
    
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
    
    listing = get_listing(seller_email, listing_ID)
    bids = get_bids(listing_ID)
    numbids = len(bids)
    # print(session["user"])

    # find latest/current bid just by maximum bid_price
    latestbid = get_latest_bid(bids)
        
    return render_template("auction_listing.html", user=session["user"], role=session["role"], seller_type=session["seller_type"], listing=listing, bids=bids, numbids=numbids, latestbid=latestbid)

@app.route("/sell_item", methods=["GET", "POST"])
def sell_item():
    if "user" not in session and session["role"] != "seller":
        return redirect(url_for("login"))
    
    categories = parse_categories(get_categories())

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
            return render_template("sell_item.html", user=session["user"], categories=categories, seller_type=session["seller_type"])
        
        # NOTE
        # listing_IDs for auction_listings seem to be randomly generated numbers in the given dataset
        # in order to insert new listings while making sure listing_IDs are unique...
        # we will keep schema as is and just increment ID numbers from the highest existing ID for each seller
        
        # E.g.
        # if a seller has 2 listings with IDs of 4 and 281...
        # making a new listing will have an ID of 282
        seller_listings = get_seller_listings(session["user"])
        listing_IDs = []
        for listing in seller_listings:
            listing_IDs.append(listing["listing_ID"])

        new_listing_ID = max(listing_IDs) + 1 # creating new listing_ID
        insert_listing(session["user"], new_listing_ID, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids)

        flash("Item successfully added!")
        return render_template("sell_item.html", user=session["user"], categories=categories, seller_type=session["seller_type"])
    
    return render_template("sell_item.html", user=session["user"], categories=categories, seller_type=session["seller_type"])

@app.route("/edit_item/<string:seller_email>/<int:listing_ID>", methods=["GET", "POST"])
def edit_item(seller_email, listing_ID):
    if "user" not in session and session["role"] != "seller":
        return redirect(url_for("login"))
    
    listing = get_listing(seller_email, listing_ID)
    categories = parse_categories(get_categories())

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
            return render_template("edit_item.html", user=session["user"], listing=listing, categories=categories, seller_type=session["seller_type"])
        
        update_listing(seller_email, listing_ID, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids)
        listing = get_listing(seller_email, listing_ID)

        flash("Item successfully updated!")
        return render_template("edit_item.html", user=session["user"], listing=listing, categories=categories, seller_type=session["seller_type"])
    
    return render_template("edit_item.html", user=session["user"], listing=listing, categories=categories, seller_type=session["seller_type"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Attempt to insert the user into the DB
        if insert_new_user(request.form):
            # AUTO-LOGIN LOGIC START
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
            # AUTO-LOGIN LOGIC END

        flash("Registration failed. Email might already exist.")
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)