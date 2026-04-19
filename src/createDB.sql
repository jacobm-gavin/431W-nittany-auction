CREATE DATABASE IF NOT EXISTS nittanyauction;
USE nittanyauction;

CREATE TABLE IF NOT EXISTS Users (
    email VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS HelpDesk (
    email VARCHAR(255) PRIMARY KEY,
    position VARCHAR(255) NOT NULL,
    FOREIGN KEY (email) REFERENCES Users(email)
);

CREATE TABLE IF NOT EXISTS Zipcode_Info (
    zipcode VARCHAR(255) PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Address (
    address_ID VARCHAR(255) PRIMARY KEY,
    zipcode VARCHAR(255) NOT NULL,
    street_num VARCHAR(255) NOT NULL,
    street_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (zipcode) REFERENCES Zipcode_Info(zipcode)
);

CREATE TABLE IF NOT EXISTS Bidders (
    email VARCHAR(255) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    home_address_id VARCHAR(255) NOT NULL,
    major VARCHAR(255) NOT NULL,
    FOREIGN KEY (home_address_id) REFERENCES Address(address_ID)
);

CREATE TABLE IF NOT EXISTS Sellers (
    email VARCHAR(255) PRIMARY KEY,
    bank_routing_number VARCHAR(255) NOT NULL,
    bank_account_number VARCHAR(255) NOT NULL,
    balance INT NOT NULL,
    FOREIGN KEY (email) REFERENCES Users(email)
);

CREATE TABLE IF NOT EXISTS Local_Vendors (
    email VARCHAR(255) PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    business_address_id VARCHAR(255) NOT NULL,
    customer_service_phone_number VARCHAR(255) NOT NULL,
    FOREIGN KEY (email) REFERENCES Sellers(email),
    FOREIGN KEY (business_address_id) REFERENCES Address(address_ID)
);

CREATE TABLE IF NOT EXISTS Requests (
    request_id INT PRIMARY KEY,
    sender_email VARCHAR(255) NOT NULL,
    helpdesk_staff_email VARCHAR(255) NOT NULL,
    request_type VARCHAR(255) NOT NULL,
    request_desc VARCHAR(255) NOT NULL,
    request_status INTEGER NOT NULL,
    FOREIGN KEY (sender_email) REFERENCES Users(email),
    FOREIGN KEY (helpdesk_staff_email) REFERENCES HelpDesk(email)
 );

CREATE TABLE IF NOT EXISTS Credit_Cards (
    credit_card_num VARCHAR(255) PRIMARY KEY,
    card_type VARCHAR(255) NOT NULL,
    expire_month INT NOT NULL,
    expire_year INT NOT NULL,
    security_code VARCHAR(255) NOT NULL,
    owner_email VARCHAR(255) NOT NULL,
    FOREIGN KEY (owner_email) REFERENCES Bidders(email)
);

CREATE TABLE IF NOT EXISTS Categories (
    parent_category VARCHAR(255),
    category_name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Auction_Listings (
    seller_email VARCHAR(255) NOT NULL,
    listing_ID INTEGER NOT NULL,
    category VARCHAR(255) NOT NULL,
    auction_title VARCHAR(255) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_description VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    reserve_price INT NOT NULL,
    max_bids INTEGER NOT NULL,
    status INTEGER NOT NULL,
    PRIMARY KEY (seller_email, listing_ID),
    FOREIGN KEY (seller_email) REFERENCES Sellers(email),
    FOREIGN KEY (category) REFERENCES Categories(category_name)
);

CREATE TABLE IF NOT EXISTS Bids (
    bid_ID INT PRIMARY KEY,
    seller_email VARCHAR(255) NOT NULL,
    listing_ID INT NOT NULL,
    bidder_email VARCHAR(255) NOT NULL,
    bid_price INT NOT NULL,
    FOREIGN KEY (seller_email, listing_ID) REFERENCES Auction_Listings(seller_email, listing_ID),
    FOREIGN KEY (bidder_email) REFERENCES Bidders(email)
);

CREATE TABLE IF NOT EXISTS Transactions (
    transaction_ID INT PRIMARY KEY,
    seller_email VARCHAR(255) NOT NULL,
    listing_ID INT NOT NULL,
    buyer_email VARCHAR(255) NOT NULL,
    date VARCHAR(255) NOT NULL,
    payment INT NOT NULL,
    FOREIGN KEY (seller_email, listing_ID) REFERENCES Auction_Listings(seller_email, listing_ID),
    FOREIGN KEY (buyer_email) REFERENCES Bidders(email)
);

CREATE TABLE IF NOT EXISTS Rating (
    bidder_email VARCHAR(255) NOT NULL,
    seller_email VARCHAR(255) NOT NULL,
    date VARCHAR(255) NOT NULL,
    rating INT NOT NULL,
    rating_desc VARCHAR(255) NOT NULL,
    PRIMARY KEY (bidder_email, seller_email, date),
    FOREIGN KEY (bidder_email) REFERENCES Bidders(email),
    FOREIGN KEY (seller_email) REFERENCES Sellers(email)
);

CREATE TABLE IF NOT EXISTS Listing_Audit (
    seller_email VARCHAR(255) NOT NULL,
    listing_ID INTEGER NOT NULL,
    remaining_bids INTEGER NOT NULL,
    removal_reason VARCHAR(255) NOT NULL,
    PRIMARY KEY (seller_email, listing_ID),
    FOREIGN KEY (seller_email, listing_ID) REFERENCES Auction_Listings(seller_email, listing_ID)
)