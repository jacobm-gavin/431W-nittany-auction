import mysql.connector
import os
from dotenv import load_dotenv
import pandas as pd
import hashlib
from sqlalchemy import create_engine

load_dotenv()
db_password = os.getenv("DB_PASSWORD")
db_url = f'mysql+pymysql://root:{db_password}@localhost:3306/nittanyauction'
print(db_url)
engine = create_engine(db_url)

standard_tables = {
    'Zipcode_Info.csv': 'zipcode_info',
    'Address.csv': 'address',
    'Bidders.csv': 'bidders',
    'Sellers.csv': 'sellers',
    'Local_Vendors.csv': 'local_vendors',
    'Helpdesk.csv': 'helpdesk',
    'Categories.csv': 'categories',
    'Auction_Listings.csv': 'auction_listings',
    'Bids.csv': 'bids',
    'Credit_Cards.csv': 'credit_cards',
    'Ratings.csv': 'rating',
    'Requests.csv': 'requests',
    'Transactions.csv': 'transactions'
}

print("Populating users...")
df_users = pd.read_csv('../dataset/Users.csv')
df_users['password'] = df_users['password'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest())
df_users.to_sql('users', con=engine, if_exists='append', index=False)

for file, table in standard_tables.items():
    print(f"Populating {table}...")
    df = pd.read_csv(f'../dataset/{file}')
    if table == 'auction_listings':
        df['Reserve_Price'] = df['Reserve_Price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip().astype(int)
    df.to_sql(table, con=engine, if_exists='append', index=False)

print("Database successfully populated")

