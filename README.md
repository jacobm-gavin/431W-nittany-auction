# NittanyAuction
Working files for 431W DB Management Project phase 1 + phase 2

## Project Description
NittanyAuction is a prototyped web application allowing users to sell, buy, and edit auction items, similarly to other shopping sites like eBay. NittanyAuction's main purpose is demonstrating the use of a relational database management system to fulfill this task.

## File Organization
`/src` - All source code for the project, including `main.py` to run the application.  
`/src/templates` - All of the raw HTML templates used for each page.  
`/public` - Any SVGs or icons  
`/dataset` - The provided dataset, including all `csv` files for populating the database.  

## Implemented Features
- User Login (Bidder/Seller/HelpDesk)
- Category Hierarchy
- Auction Listing Management (Sellers)
    - Seller Home Page
    - Editing/Removing Listings
    - Preserving Historical Information
- Auction Bidding (Bidders)
    - Bidding Rules/Restrictions
    - Auction Completion and Notifications  
    - Payment Flow  
- User Registration
- User Profile Update
- Product Search
- Ratings

## Links
- [Team Contract](https://pennstateoffice365-my.sharepoint.com/:w:/r/personal/jam9201_psu_edu/_layouts/15/Doc.aspx?sourcedoc=%7B524cc132-0567-45f7-85a8-2b2d145660ef%7D&action=edit&wdLOR=c2DC118A9-E1A5-C049-B526-AB67AB616484&wdPid=777d90ac)
- [Final Report](https://pennstateoffice365-my.sharepoint.com/:w:/r/personal/jmg7896_psu_edu/_layouts/15/Doc.aspx?sourcedoc=%7B91FA7E13-9488-45CC-8F09-6B7A5FBADC71%7D&file=Document%201.docx&action=editNew&mobileredirect=true&wdOrigin=WAC.WORD.HOME-BUTTON%2CAPPHOME-WEB.BANNER.NEWBLANK&wdPreviousSession=fef1d5eb-53eb-43ce-005d-9957e38b5a84&wdPreviousSessionSrc=Wac&ct=1770923261069)
- [ER Diagram](https://lucid.app/lucidchart/cd99062f-3bf8-4db4-ad9c-1ccaa2d93d91/edit?viewport_loc=-1181%2C34%2C2201%2C2273%2C0_0&invitationId=inv_2fac177f-5c99-4214-b183-7dc5f7f3923c)

## Tech Stack
- **Web framework**: Flask
- **Language**: Python
- **DB**: MySQL
- **CSS framework**: Bootstrap

## Database Setup

1. Install MySQL Community from https://dev.mysql.com/downloads/mysql/. When installing, you can leave all configurations as default. 
    - Additionally, when making users during setup, we would just recommend making an admin user.
    - Installation will include creation of a password on your local machine, so be sure to remember this. (We will write it down and save it in a later step.)


2. Clone this repository in whichever folder you'd like using `git clone https://github.com/jacobm-gavin/431W-nittany-auction`


3. Open up this repository in PyCharm, and install Pycharm if not already installed (again, leaving all default configurations is usually fine).


4. Once open in PyCharm, click the databases tab on the right.


5. Click the add button under 'Database' and add a MySQL 'Data Source'. You can name this whatever you want, such as 'db' or 'nittanyauction.' Here, just make sure to add in a user and your password you set up with MySQL from earlier.
    - The other information such as port should be already configured to the default if you also set up MySQL with the default configurations.


6. In PyCharm, run the `createDB.sql` file.


7. Open up the terminal in the bottom left of PyCharm. Make sure you are in the correct directory for the repository, and run the following command: `pip install pandas sqlalchemy pymysql dotenv mysql-connector-python`. All this does is just install the correct dependencies to run any Python files such as `populateDB.py` or `main.py`. 
    - If you have any errors, open up any files with imports that are failing. Just click on them and PyCharm will have a button to install the missing dependency.


8. In PyCharm, create a new file in the root directory called `.env`. Open `.env`, and paste in `DB_PASSWORD={YOUR_DB_PASSWORD_HERE}`, replacing `{YOUR_DB_PASSWORD_HERE}` with your previously configured MySQL password. 


9. Run `populateDB.py`. At the conclusion of running `populateDB.py`, you should see a message saying "Database successfully populated". 
    - To double check, click on your 'nittanyauction' database in the database tab, click on new, and add a new query console. Try a simple SQL query like `SELECT * FROM nittanyauction.users`. You should now see your database is populated.

## How to Run NittanyAuction

1. Run `main.py`.


2. In the terminal, you should see no errors and a link to the port on your localhost where the application is being run. Click this to open it in your browser.
