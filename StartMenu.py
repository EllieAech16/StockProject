
import sys
import os
import sqlite3
import _sqlite3

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.uic import *
from PyQt5.QtWidgets import QMessageBox

import hashlib

from WebScraping import *
from StockPageTemplate import *#StockButton
from WebScraping import StockData
from AccountPage import *

from functools import *

######## Importing Libaries #########


class Login():
    """Login class, allows a user to log in with GUI"""
    def __init__(self):
        self.validpassword = ''
        self.currentemail = ''
        self.currentpassword = ''
        self.loggedin = []
        #declaring variables 


    def login_validation(self, currentemail, currentpassword):
        '''checks details enetered with details held in the database'''
        
        self.currentemail = currentemail
        self.currentpassword = currentpassword
        failure_reason = ''

        
        try:
            conn = sqlite3.connect('NEA.db', isolation_level=None) #connect to database
            
            cursor = conn.cursor() # create a cursor to execute commands
            
            print("Database connected") #shows message when connected to database


        except:
            print('Database connection error')#if an error occurs during the connection this will be outputted


        try:
            #retrieves data from database
            getuserpass = ('''SELECT Password FROM UserInfo WHERE Email = ? ''')#sql query to select password from database
            
            cursor.execute(getuserpass, (self.currentemail,)) #executes the sql statement based on the data
            
            self.validpassword = cursor.fetchmany(1)#retrives one result 


            #hashes entered password
            encoded_password = hashlib.md5(currentpassword.encode())#md5 hash function encodes
            
            hashed_password = encoded_password.hexdigest()#converts the encoded hash to hex


            #compares the hashed password entered to the hashed password in the database
            if hashed_password == self.validpassword[0][0]: #compares the value retrieved from db to inputted
                self.loggedin.append(True) #if passwords match - logs in
                
            else:
                self.loggedin.append(False)

            
        except:
            self.loggedin.append(False)
                
                
        return self.loggedin




    def get_userID(self):
        '''Retrieves the current users ID'''
        
        try:
            conn = sqlite3.connect('NEA.db', isolation_level=None) #connect to database
            
            cursor = conn.cursor() # create a cursor to execute commands
            
            print("Database connected") #shows message when connected to database
            

        except:
            print('Database connection error')#if an error occurs during the connection this will be outputted

        
        get_userID_sql = ('''SELECT UserID FROM UserInfo WHERE Email = ? ''')
        
        cursor.execute(get_userID_sql, (str(self.currentemail),))
        
        temp_userID = cursor.fetchmany(1)#retrieves one result
        
        current_userID = temp_userID[0][0]
        
        return current_userID




    def make_database(self):
        '''Creates the NEA database with all tables'''
        
        conn = sqlite3.connect('NEA.db')
        
        cursor = conn.cursor()

        #creates StockChange Table
        cursor.execute(''' CREATE TABLE IF NOT EXISTS StockChange ( ChangeEventID INTEGER NOT NULL UNIQUE,
                        StockID INTEGER NOT NULL, Change REAL NOT NULL, PercentChange REAL NOT NULL,
                        ChangeDateTime TEXT NOT NULL, PRIMARY KEY(ChangeEventID AUTOINCREMENT) )''')


        #creates StockIdentification Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS StockIdentification (StockID INTEGER NOT NULL UNIQUE,
                        StockName TEXT NOT NULL UNIQUE, StockSymbol TEXT, PRIMARY KEY(StockID AUTOINCREMENT) )''')


        #creates StockPrice Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS StockPrice ( PriceEventID INTEGER NOT NULL UNIQUE,
                        StockID INTEGER NOT NULL, Price REAL NOT NULL, PriceDateTime TEXT NOT NULL,
                        FOREIGN KEY(StockID) REFERENCES StockIdentification(StockID),
                        PRIMARY KEY(PriceEventID AUTOINCREMENT) )''')


        #creates StockVolume Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS StockVolume ( VolumeEventID INTEGER NOT NULL UNIQUE,
                        StockID INTEGER NOT NULL, Volume INTEGER NOT NULL, VolumeDateTime TEXT NOT NULL,
                        FOREIGN KEY(StockID) REFERENCES StockIdentification(StockID),
                        PRIMARY KEY(VolumeEventID AUTOINCREMENT) ) ''')
                

        #creates UserInfo Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS UserInfo ( UserID INTEGER NOT NULL UNIQUE,
                        Firstname TEXT NOT NULL, LastName TEXT NOT NULL, Email TEXT NOT NULL UNIQUE,
                        Password TEXT NOT NULL, PRIMARY KEY(UserID AUTOINCREMENT) ) ''')


        #creates UserStocks table
        cursor.execute('''CREATE TABLE IF NOT EXISTS UserStocks ( UserID INTEGER NOT NULL,
                        StockID INTEGER NOT NULL, PRIMARY KEY(UserID,StockID), FOREIGN KEY(UserID)
                        REFERENCES UserInfo(UserID), FOREIGN KEY(StockID) REFERENCES StockIdentification(StockID) ) ''')


        

class LoginDisplay(QWidget):
    ''' Creates Main Display when logging in '''


    def __init__(self):
        '''Initialises variables'''
        super().__init__()
        self.setWindowTitle('Login')
        self.resize(500,120)#sets window size
        self.login_obj = Login()
        self.check_database()
        self.init_UI()#calls function which initialises the display
        self.setLayout(self.grid_layout)#sets the layout for the page to be in grid format


        

    def init_UI(self):
        '''initialises each element of the page on a window'''
        self.grid_layout = QGridLayout()#calls layout 

        login_lbl = QLabel('<font size = "12"> Login </font>')#initialises login label
        self.grid_layout.addWidget(login_lbl, 0, 0)#places the label on the grid

        email_lbl = QLabel('<font size = "10"> Email </font>')#initialises email label
        self.email_le = QLineEdit()#initialises line edit
        self.email_le.setPlaceholderText('Enter your email')#sets text in the line edit to instruct user
        self.grid_layout.addWidget(email_lbl, 1, 0)#places the label on the grid
        self.grid_layout.addWidget(self.email_le, 1, 1)#places the line edit on the grid

                        
        password_lbl = QLabel('<font size = "10"> Password </font>')#initialises password label
        self.password_le = QLineEdit()
        self.password_le.setPlaceholderText('Enter your password')
        self.password_le.setEchoMode(QLineEdit.Password)#hides the text typed in by the user
        self.password_hidden = True #sets default password view to hidden
        self.grid_layout.addWidget(password_lbl, 2, 0)
        self.grid_layout.addWidget(self.password_le, 2, 1)

        self.view_btn = QPushButton('View')#initialises button for viewing password
        self.view_btn.clicked.connect(self.switch_state)
        self.grid_layout.addWidget(self.view_btn, 2,2)
        

        self.login_btn = QPushButton('Login')#initialises a button for login
        self.login_btn.clicked.connect(self.validate_details)#calls validate_details function when pressed 
        self.grid_layout.addWidget(self.login_btn, 3, 1)


        self.signup_btn = QPushButton('Sign Up')#initialises a button for acessing the sign up page
        self.signup_btn.clicked.connect(self.go_to_signup)#calls the function go_to_signup when pressed
        self.grid_layout.addWidget(self.signup_btn, 3,2)




    def check_database(self):
        '''Checks to see if the NEA file is created, and contains tables inside'''
        
        try:
            conn = sqlite3.connect('NEA.db', isolation_level=None) #connect to database
            cursor = conn.cursor() # create a cursor to execute commands
            print("Database connected") #shows message when connected to database

        except:
            print('Database connection error')#if an error occurs during the connection this will be outputted

        try:
            check_db_sql = '''SELECT UserID FROM UserInfo LIMIT 1;'''#attempts to retrieve a record 
            
            cursor.execute(check_db_sql)#executes SQL command
            
            table_exist = cursor.fetchone()
            
        except:
            self.login_obj.make_database()

        
        

    def validate_details(self):
        '''checks if logged in correctly'''
        
        currentemail = self.email_le.text()#sets to text entered
        
        currentpassword = self.password_le.text()#sets to text entered

        self.login_obj.login_validation(currentemail, currentpassword)#calling method from login class 

        if self.login_obj.loggedin[-1] == True: #if function returns true the user is valid
            QMessageBox.about(self, 'Login', 'Sucess')#displays message box

            self.userID = self.login_obj.get_userID()
            
            self.go_to_main()#creates an instance of the main menu page
            

        else:
            QMessageBox.about(self, 'Login', 'Incorrect Email or Password')




    def go_to_signup(self):
        '''creates object of signupdisplay'''
        self.signup_obj = SignUpDisplay()
        self.signup_obj.show()
        self.close()


    def go_to_main(self):
        '''Opens Main Display '''
        self.main_gui_display_obj = MainGuiDisplay(self.userID)
        self.main_gui_display_obj.show()
        self.close()


    def switch_state(self):
        '''makes password viewable/hidden'''
        
        if self.password_hidden == True:
            self.password_le.setEchoMode(QLineEdit.Normal)
            self.password_hidden = not(self.password_hidden)

        else:
            self.password_le.setEchoMode(QLineEdit.Password)
            self.password_hidden = not(self.password_hidden)

            


class Signup():
    '''Signup class, runs signup page and validates '''
    
    def __init__(self):
        self.usr_firstname = ''
        self.usr_lastname= ''
        self.usr_email = ''
        self.usr_password = ''
        self.validation_result = False
        self.validation_message = ''
        #initialises variables
        

    def signup_validation(self, usr_firstname, usr_lastname, usr_email, usr_password):
        self.usr_firstname = str(usr_firstname)
        self.usr_lastname = str(usr_lastname)
        self.usr_email = str(usr_email)
        self.usr_password = str(usr_password)

        
        if ('@'and ('.com' or '.co.uk' or '.ac.uk') in self.usr_email) and (len(self.usr_password) >= 8): #ensures the  email is in a valid format and the password is a secure length
            self.validation_result = True #returns if valid


        elif '@' not in self.usr_email: #checks for invalid email format and returns correct message
            self.validation_result = False
            self.validation_message = 'Email format is invalid, please try again.'
            return self.validation_message
        

        elif ('.com' or '.co.uk' or '.ac.uk') not in self.usr_email:#checks for invalid email format and returns correct message
            self.validation_result = False
            self.validation_message = 'Email format is invalid, please try again.'
            return self.validation_message


        elif len(self.usr_password) < 8:#checks for invalid password length and returns correct message
            self.validation_result = False
            self.validation_message = 'Password must be at least 8 characters.'
            return self.validation_message
        
        return self.validation_result
        


        
    def add_user(self, usr_firstname, usr_lastname, usr_email, usr_password):
        '''adds a new user to the database'''
        self.usr_firstname = usr_firstname
        self.usr_lastname = usr_lastname
        self.usr_email = usr_email
        self.usr_password = usr_password

        
        try:
            conn = sqlite3.connect('NEA.db', isolation_level=None) #connect to database
            cursor = conn.cursor() # create a cursor to execute commands
            print("Database connected")

        except:
            print('Database connection error')

            
        insert_validuser_sql = """INSERT INTO UserInfo(FirstName, LastName, Email, Password) 
                                VALUES(?, ?, ?, ?);""" #sets SQL command

        #hashes password to be stored in database
        usr_encoded_password = hashlib.md5(self.usr_password.encode())#md5 hash function encodes 
        hashed_usr_password = usr_encoded_password.hexdigest()#converts the encoded hash to hex

        insert_validuser_data = (self.usr_firstname, self.usr_lastname, self.usr_email, hashed_usr_password) #adds data to command
                
        cursor.execute(insert_validuser_sql, insert_validuser_data)#executes SQL command
        
        conn.commit()
        
        validation_result = 'Sucess'




class SignUpDisplay(QWidget):
    '''Creates sign up display if account not possesed'''

    def __init__(self):
        '''initialises variables'''
        super().__init__()
        self.setWindowTitle('Sign Up')
        self.resize(600,300)
        self.init_UI()
        self.setLayout(self.grid_layout)
        self.signup_obj = Signup()
        self.signedin = []

        
    def init_UI(self):
        self.grid_layout = QGridLayout()

        #creates signup label
        self.signup_lbl = QLabel('<font size = "12"> Sign Up </font>')
        self.grid_layout.addWidget(self.signup_lbl, 0, 1)


        #creates label and line edit for first name
        self.first_name_lbl = QLabel('<font size = "10"> First Name </font>')
        self.first_name_le = QLineEdit()
        self.first_name_le.setPlaceholderText('Enter your first name')#sets placeholder text for line edit
        self.grid_layout.addWidget(self.first_name_lbl, 1, 0)
        self.grid_layout.addWidget(self.first_name_le, 1, 1)


        #creates label and line edit for last name
        self.last_name_lbl = QLabel('<font size = "10"> Last Name </font>')
        self.last_name_le = QLineEdit()
        self.last_name_le.setPlaceholderText('Enter your last name')
        self.grid_layout.addWidget(self.last_name_lbl, 2, 0)
        self.grid_layout.addWidget(self.last_name_le, 2, 1)
        

        #creates label and line edit for email
        self.email_lbl = QLabel('<font size = "10"> Email </font>')
        self.email_le = QLineEdit()
        self.email_le.setPlaceholderText('Enter your email')
        self.grid_layout.addWidget(self.email_lbl, 3, 0)
        self.grid_layout.addWidget(self.email_le, 3, 1)


        #creates label and line edit for password
        self.password_lbl = QLabel('<font size = "10"> Password </font>')
        self.password_le = QLineEdit()
        self.password_le.setPlaceholderText('Enter your password')
        self.password_le.setEchoMode(QLineEdit.Password) #sets password line edit to hidden
        self.password_hidden = True #sets password edit default to hidden
        self.grid_layout.addWidget(self.password_lbl, 4, 0)
        self.grid_layout.addWidget(self.password_le, 4, 1)


        #creates and connects button to view/hide password
        self.view_btn = QPushButton('View')#initialises button for viewing password
        self.view_btn.clicked.connect(self.switch_state)
        self.grid_layout.addWidget(self.view_btn, 4,2)

        #creates and connects button to sign up 
        self.signup_btn = QPushButton('Sign Up')
        self.signup_btn.clicked.connect(self.validate_signup)
        self.grid_layout.addWidget(self.signup_btn,5,1)




    def validate_signup(self):
        '''checks if signup details are valid, if so adds user and goes to main'''
        usr_firstname = self.first_name_le.text()
        usr_lastname = self.last_name_le.text()
        usr_email = self.email_le.text()
        usr_password = self.password_le.text()
        
        valid = self.signup_obj.signup_validation(usr_firstname, usr_lastname, usr_email, usr_password) #passes current details to validation

        #if details are valid, adds details to database and creates an instance of the main menu
        if valid == True:
            try:
                self.signup_obj.add_user(usr_firstname, usr_lastname, usr_email, usr_password)
                
            except:
                self.make_database()
                self.signup_obj.add_user(usr_firstname, usr_lastname, usr_email, usr_password)
                
            self.signedin.append(True) #appends to signed in, allows for later retrival of user ID

            self.userID = self.get_userID(usr_email)

            self.go_to_main()

            
        else:
            QMessageBox.about(self, 'Sign Up', str(valid))



            
    def switch_state(self):
        '''makes password viewable/hidden'''
        
        if self.password_hidden == True:
            self.password_le.setEchoMode(QLineEdit.Normal)
            self.password_hidden = not(self.password_hidden)

        else:
            self.password_le.setEchoMode(QLineEdit.Password)
            self.password_hidden = not(self.password_hidden)




    def go_to_main(self):
        'creates and displays an instance of the main menu display'
        self.main_gui_display_obj = MainGuiDisplay(self.userID)#creates a instance of main gui display while passing the user ID
        self.main_gui_display_obj.show()#shows the display
        self.close()




    def make_database(self):
        '''creates databases if prompted to in the signup classes '''
        conn = sqlite3.connect('NEA.db')
        cursor = conn.cursor()

        #creates StockChange table
        cursor.execute(''' CREATE TABLE IF NOT EXISTS StockChange ( ChangeEventID INTEGER NOT NULL UNIQUE,
                        StockID INTEGER NOT NULL, Change REAL NOT NULL, PercentChange REAL NOT NULL,
                        ChangeDateTime TEXT NOT NULL, PRIMARY KEY(ChangeEventID AUTOINCREMENT) )''')


        #creates StockIdentification table
        cursor.execute('''CREATE TABLE IF NOT EXISTS StockIdentification (StockID INTEGER NOT NULL UNIQUE,
                        StockName TEXT NOT NULL UNIQUE, StockSymbol TEXT, PRIMARY KEY(StockID AUTOINCREMENT) )''')


        #creates StockPrice table
        cursor.execute('''CREATE TABLE IF NOT EXISTS StockPrice ( PriceEventID INTEGER NOT NULL UNIQUE,
                        StockID INTEGER NOT NULL, Price REAL NOT NULL, PriceDateTime TEXT NOT NULL,
                        FOREIGN KEY(StockID) REFERENCES StockIdentification(StockID),
                        PRIMARY KEY(PriceEventID AUTOINCREMENT) )''')


        #creates StockVolume table
        cursor.execute('''CREATE TABLE IF NOT EXISTS StockVolume ( VolumeEventID INTEGER NOT NULL UNIQUE,
                        StockID INTEGER NOT NULL, Volume INTEGER NOT NULL, VolumeDateTime TEXT NOT NULL,
                        FOREIGN KEY(StockID) REFERENCES StockIdentification(StockID),
                        PRIMARY KEY(VolumeEventID AUTOINCREMENT) ) ''')

                
        #creayes userinfo table
        cursor.execute('''CREATE TABLE IF NOT EXISTS UserInfo ( UserID INTEGER NOT NULL UNIQUE,
                        Firstname TEXT NOT NULL, LastName TEXT NOT NULL, Email TEXT NOT NULL UNIQUE,
                        Password TEXT NOT NULL, PRIMARY KEY(UserID AUTOINCREMENT) ) ''')

        
        #creates user stocks table
        cursor.execute('''CREATE TABLE IF NOT EXISTS UserStocks ( UserID INTEGER NOT NULL,
                        StockID INTEGER NOT NULL, PRIMARY KEY(UserID,StockID), FOREIGN KEY(UserID)
                        REFERENCES UserInfo(UserID), FOREIGN KEY(StockID) REFERENCES StockIdentification(StockID) ) ''') 


    

    def get_userID(self, usr_email):
        '''gets current user ID after signup'''
        
        try:
            conn = sqlite3.connect('NEA.db', isolation_level=None) #connect to database
            cursor = conn.cursor() # create a cursor to execute commands
            print("Database connected")

        except:
            print('Database connection error')

        
        current_userID_sql = """SELECT UserID FROM UserInfo WHERE Email = ?"""
        
        current_userID_data = usr_email

        cursor.execute(current_userID_sql, (current_userID_data,))#executes SQL command

        temp_userID = cursor.fetchmany(1)

        current_userID = temp_userID[0][0]
 
        return current_userID
        
    





class MainGuiDisplay(QWidget):
    '''Creates the menu display as well as interactions with stocks'''
    
    def __init__(self, passedID):
        super().__init__()
        self.resize (1100,800)
        self.setWindowTitle('Stock Monitoring')
        self.current_user_ID = passedID
        
        self.account_details_obj = AccountDetailsPage(self.current_user_ID)
        self.get_user_details()

        self.stock_data_obj = StockData()
        self.initial_refresh()
        
        self.init_UI()


    def click_connector(self, index):
        '''connects buttons function'''
        self.button_list[index].view_stock_page()#displays stock page of button pressed


    def init_UI(self):
        '''initialises UI'''
        mainlayout = QGridLayout()
        vlayout = QVBoxLayout()


        ##watchlist tab##
        self.watchlist_tab = QScrollArea()#creates a scrollable area
        self.watchlist_widget = QWidget()
        self.grid_layout = QGridLayout()

        
        #creates a label for watchlist title 
        watchlist_lbl = QLabel("Watchlist")
        watchlist_lbl.setFont(QFont('Arial', 18))
        self.grid_layout.addWidget(watchlist_lbl, 0 , 0)


        #creates and connects the refresh button to refresh the watchlsit
        refresh_watchlist_btn = QPushButton('Refresh')
        self.grid_layout.addWidget(refresh_watchlist_btn, 0, 2 )
        refresh_watchlist_btn.clicked.connect(self.refresh_check)


        #retrieves all users stocks with passed ID
        self.stock_data_obj.get_user_stocks(self.current_user_ID)


        #creates lists for iteration in order to create labels
        watchlist_symbol_list = self.stock_data_obj.get_user_stock_symbol()#retrieves symbols of users stocks
        watchlist_name_list = self.stock_data_obj.get_user_stock_name()#retrieves names of users stocks
        watchlist_price_list = self.stock_data_obj.get_user_stock_price()#retrieves prices of users stocks


        #iterates through symbol list and creates a label for each
        for symbol in watchlist_symbol_list:
            symbol_label = QLabel(symbol)
            self.grid_layout.addWidget(symbol_label, (watchlist_symbol_list.index(symbol)+1) ,0)


        #iterates through name list and creates a label for each
        for name in watchlist_name_list:
            name_label = QLabel(name)
            self.grid_layout.addWidget(name_label, (watchlist_name_list.index(name)+1) ,1)


        #iterates through price list and creates a label for each
        for price in watchlist_price_list:
            price_label = QLabel(str(price[0][0]) + 'p')
            self.grid_layout.addWidget(price_label, (watchlist_price_list.index(price)+1) ,2)


        self.user_stock_list = self.stock_data_obj.get_user_stockID()#retrieves stock list
        self.watchlist_button_list = []


        #iterates through the users stocks, creating a button for each that when clicked, will instantiate a unique stock page for the stock 
        index_2 = 1
        for ID in self.user_stock_list:
            stock_button = StockButton(ID, self.current_user_ID, self) #creates stock button object passing unique ID though

            self.watchlist_button_list.append(stock_button)#appends the button to a list to store in memory (without this, buttons would not be able to be called)

            watchlist_connector_partial = partial(self.click_connector, (index_2 -1))#creates a partial to connect each button to their function
            
            self.watchlist_button_list[-1].viewstock_btn.clicked.connect(watchlist_connector_partial)#connects each button
            
            self.grid_layout.addWidget(self.watchlist_button_list[(index_2 - 1)].viewstock_btn, index_2, 4)#adds widget
            
            index_2 += 1


        #sets watchlist layout
        self.watchlist_widget.setLayout(self.grid_layout)
        self.watchlist_tab.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)#adds scroll bar 
        self.watchlist_tab.setWidget(self.watchlist_widget)




        ##FTSE 100 tab##
        self.ftse_tab = QScrollArea()
        self.ftse_widget = QWidget()
        self.grid_layout = QGridLayout()

        #creates title label
        FTSE_lbl = QLabel("FTSE 100")
        FTSE_lbl.setFont(QFont('Arial', 18))
        self.grid_layout.addWidget(FTSE_lbl, 0 , 0)

        #creates and connects refresh button for the FTSE 100 list
        refresh_ftse_btn = QPushButton('Refresh')
        self.grid_layout.addWidget(refresh_ftse_btn, 0, 2 )
        refresh_ftse_btn.clicked.connect(self.refresh_check)
        

        #gets all stock IDs from all stocks
        self.stockID_list = self.stock_data_obj.get_all_stockIDs()

        index  = 1
        self.button_list = []

        #iterates through the users stocks, creating a button for each that when clicked, will instantiate a unique stock page for the stock 
        for ID in self.stockID_list:
            stock_button = StockButton(ID[0], self.current_user_ID, self)#creates stock button object passing unique ID though           
            
            self.button_list.append(stock_button)#appends the button to a list to store in memory (without this, buttons would not be able to be called)               
            
            connector_partial = partial(self.click_connector, index-1)#creates a partial to connect each button to their function
                                
            self.button_list[-1].viewstock_btn.clicked.connect(connector_partial)#connects each button
                                 
            self.grid_layout.addWidget(self.button_list[index - 1].viewstock_btn, index, 5)#adds widget
                      
            index += 1



        #creates lists for iteration in order to create labels
        self.stock_data_obj.get_stock_info()
        ftse_price_list = self.stock_data_obj.get_price_list()
        ftse_name_list = self.stock_data_obj.get_name_list()
        ftse_symbol_list = self.stock_data_obj.get_symbol_list()
        ftse_price_change_list = self.stock_data_obj.get_price_change_list()
        ftse_price_change_percent_list = self.stock_data_obj.get_price_change_percent_list()


        #iterates through symbol list and creates a label for each item
        for item in ftse_symbol_list:
            symbol_label = QLabel(item)
            self.grid_layout.addWidget(symbol_label, (ftse_symbol_list.index(item)+1) ,0)

            
        #iterates through name list and creates a label for each item
        for item in ftse_name_list:
            name_label = QLabel(item)
            self.grid_layout.addWidget(name_label, (ftse_name_list.index(item)+1) ,1)

            
        #iterates through price list and creates a label for each item
        price_index = 1
        for item in ftse_price_list:
            price_label = QLabel(item + 'p')
            self.grid_layout.addWidget(price_label, price_index ,2)
            price_index += 1
            

        #iterates through change list and creates a label for each item
        change_index = 1
        for change in ftse_price_change_list:
            change_label = QLabel(change + 'p')
            self.grid_layout.addWidget(change_label, change_index ,3)
            change_index += 1
                                     

        #iterates through percent change list and creates a label for each item
        percent_change_index = 1 
        for percent_change in ftse_price_change_percent_list:
            percent_change_label = QLabel(percent_change)
            self.grid_layout.addWidget(percent_change_label, percent_change_index ,4)
            percent_change_index += 1
            

        #sets layout for ftse 100 page
        self.ftse_widget.setLayout(self.grid_layout)
        self.ftse_tab.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)#sets verticle scroll bar
        self.ftse_tab.setWidget(self.ftse_widget)




        ##Account details tab##
                                     
        self.accounts_tab = QWidget()
        self.accounts_tab.layout = QVBoxLayout()

        #adds title for account details page          
        self.accounts_tab.layout.addWidget(QLabel('<font size = "10"> Account Details </font>'))

        self.accounts_tab.setLayout(self.accounts_tab.layout)


        #creates and connects button for logging out
        self.log_out_btn = QPushButton('Log Out')
        self.log_out_btn.clicked.connect(self.go_to_logout)
        self.accounts_tab.layout.addWidget(self.log_out_btn)
                                     
        
        ##Initialises display for first name editing
        #creates label and line edit for changing first name as well as a button to implement the change                        
        self.first_name_lbl = QLabel('<font size = "10"> First Name </font>')
        self.accounts_tab.layout.addWidget(self.first_name_lbl)
        self.first_name_le = QLineEdit()
        self.first_name_le.setPlaceholderText(self.current_first_name)#sets placeholder value in the line edit
                                     
        self.edit_first_name_btn = QPushButton('Change')#creates button
        self.edit_first_name_btn.clicked.connect(self.change_first_name) #when pressed will call function change_first_name
        
        self.accounts_tab.layout.addWidget(self.first_name_le)#adds widget (line edit) to page layout 
        self.accounts_tab.layout.addWidget(self.edit_first_name_btn)
    


        ##Initialises display for last name editing
        #Creates a label and line edit for changing last name, as well as a change button
        self.last_name_lbl = QLabel('<font size = "10"> Last Name </font>')
        self.accounts_tab.layout.addWidget(self.last_name_lbl)

        self.last_name_le = QLineEdit()
        self.last_name_le.setPlaceholderText(self.current_last_name)
        
        self.edit_last_name_btn = QPushButton('Change')
        self.edit_last_name_btn.clicked.connect(self.change_last_name)
        
        self.accounts_tab.layout.addWidget(self.last_name_le)
        self.accounts_tab.layout.addWidget(self.edit_last_name_btn)
        


        ##Initialises display for email editing
        #Creates a label and line edit for changing email, as well as a change button
        self.email_lbl = QLabel('<font size = "10"> Email </font>')
        self.accounts_tab.layout.addWidget(self.email_lbl)

        self.email_le = QLineEdit()
        self.email_le.setPlaceholderText(self.current_email)
            
        self.edit_email_btn = QPushButton('Change')
        self.edit_email_btn.clicked.connect(self.validate_email)
      
        self.accounts_tab.layout.addWidget(self.email_le)
        self.accounts_tab.layout.addWidget(self.edit_email_btn)



        #Initialises display for password editing
        #Creates a label and line edit for changing password, as well as a change button
        self.password_lbl = QLabel('<font size = "10"> Password </font>')
        self.accounts_tab.layout.addWidget(self.password_lbl)

        self.password_le = QLineEdit()
        self.password_le.setPlaceholderText('Password')#sets default text in the line edit to Password
        self.password_le.setEchoMode(QLineEdit.Password)#sets line edit to password mode
        self.password_hidden = True #sets default password mode to hide text
                                     
        self.view_btn = QPushButton('View')#initialises button for viewing password
        self.view_btn.clicked.connect(self.switch_state)
        self.accounts_tab.layout.addWidget(self.password_le)
        self.accounts_tab.layout.addWidget(self.view_btn)
            
        self.edit_password_btn = QPushButton('Change')
        self.edit_password_btn.clicked.connect(self.validate_password)
        self.accounts_tab.layout.addWidget(self.edit_password_btn)



        #setting tabs
        self.maintab = QTabWidget()
        self.maintab.addTab(self.watchlist_tab, 'Watch List')
        self.maintab.addTab(self.ftse_tab, 'FTSE 100')
        self.maintab.addTab(self.accounts_tab, 'Account Details')

        mainlayout.addWidget(self.maintab, 0,0)
        self.setLayout(mainlayout)


        
    def get_user_details(self):
        '''retrieves current user details and seperates them '''
        self.current_details = self.account_details_obj.get_current_user_details()#retrieves all user details for editing
        self.current_first_name = self.current_details[0][0]#indexes to find each item, always in the same order
        self.current_last_name = self.current_details[0][1]
        self.current_email = self.current_details[0][2]

                 

    def go_to_logout(self):
        '''goes to log out function'''
        restart_program()#restarts program
    

    def change_first_name(self):
        '''changes users first name according to input '''
        self.current_first_name = self.first_name_le.text()
        self.first_name_le.setPlaceholderText(self.current_first_name)#sets placeholder text to updated name
        self.account_details_obj.change_first_name_db(self.current_first_name)#updates database of change
        self.first_name_le.clear()
        QMessageBox.about(self, 'Name', 'Changed')#displays message box


    def change_last_name(self):
        '''changes users last name according to input '''
        self.current_last_name = self.last_name_le.text()
        self.last_name_le.setPlaceholderText(self.current_last_name)#sets placeholder text to updated name
        self.account_details_obj.change_last_name_db(self.current_last_name)#updates database of change
        self.last_name_le.clear()
        QMessageBox.about(self, 'Name', 'Changed')#displays message box
        


    def validate_password(self):
        ''' Checks password is valid'''
        self.current_password = self.password_le.text()

        #checks password length 
        if len(self.current_password) < 8:
            self.validation = False

        elif len(self.current_password) >= 8:
            self.validation = True

        self.change_password(self.current_password, self.validation)#attemps to change password

   
    def change_password(self, current_password, validation):
        '''changes users password according to input '''
        self.current_password = current_password
        self.validation = validation

        if self.validation == True:
            self.account_details_obj.change_password_db(self.current_password)#if password is valid, the database updates
            self.password_le.clear()
            QMessageBox.about(self, 'Password', 'Changed')#displays message box
            
        elif self.validation == False:
            self.password_le.setPlaceholderText('Invalid Password, Please try again')#if password invalid , placeholder updates to error message
            QMessageBox.about(self, 'Invalid', 'Invalid Password')#displays message box
            self.password_le.clear()


    def switch_state(self):
        '''makes password viewable/hidden'''
        if self.password_hidden == True:
            self.password_le.setEchoMode(QLineEdit.Normal)
            self.password_hidden = not(self.password_hidden)

        else:
            self.password_le.setEchoMode(QLineEdit.Password)
            self.password_hidden = not(self.password_hidden)



    def validate_email(self):
        '''checks the email is valid for changing'''
        
        self.current_email = self.email_le.text()

        if ('@' and ('.com' or '.co.uk' or '.ac.uk') not in  self.current_email):
            self.validation = False
            
        elif ('@' and ('.com' or '.co.uk' or '.ac.uk') in  self.current_email):
            self.validation = True

        self.change_email(self.current_email, self.validation)
        
            
            
    def change_email(self, current_email, validation):
        '''changes users email according to input '''

        self.current_email = current_email
        self.validation = validation

        if self.validation == True:
            self.account_details_obj.change_email_db(self.current_email)#updates database
            self.email_le.setPlaceholderText(self.current_email)#sets placeholder as updated email
            self.email_le.clear()
            QMessageBox.about(self, 'Email', 'Changed')#displays message box

            
        elif self.validation == False:
            self.email_le.setPlaceholderText('Invalid Email, Please try again')#if ihnvalid, displays error in line edit
            QMessageBox.about(self, 'Invalid', 'Invalid Email')#displays message box
            self.email_le.clear()

    def initial_refresh(self):
        '''carries out initial refresh when the user first logs in'''

        ##make loading screen pop up
        QMessageBox.about(self, 'Loading', 'Please Wait')
        
        self.stock_data_obj.get_stock_info()#gets current info from web source

        
        need_refresh = self.stock_data_obj.check_names_symbols()#checks if updated needed

        
        if need_refresh == True:
            self.stock_data_obj.append_names_symbols()#appends updated name and symbols if out of date
            self.stock_data_obj.get_stock_volume()#web scrapes volume
            self.stock_data_obj.append_price_vol()#appends updated price and volume if out of date
            
            
        elif need_refresh == False:
            self.stock_data_obj.get_stock_volume()#web scrapes volume
            self.stock_data_obj.append_price_vol()#appends updated price and volume if out of date

        
    def refresh_check(self):
        '''Checks if current data needs to be refreshed '''
        
        self.stock_data_obj.get_stock_info()#gets current info from web source
        
        need_refresh = self.stock_data_obj.check_names_symbols()#checks if updated needed
        
        if need_refresh == True:
            QMessageBox.about(self, 'Loading', 'Please Wait')
            self.stock_data_obj.append_names_symbols()#appends updated name and symbols if out of date
            self.stock_data_obj.get_stock_volume()#web scrapes volume
            self.stock_data_obj.append_price_vol()#appends updated price and volume 
            
            update_display(self.current_user_ID)#updates the current display 
            self.close()#closes current window
            
            
        elif need_refresh == False:
            QMessageBox.about(self, 'Loading', 'Please Wait')
            self.stock_data_obj.get_stock_volume()#web scrapes volume
            self.stock_data_obj.append_price_vol()#appends updated price and volume 
            
            update_display(self.current_user_ID)#updates the current display
            self.close()#closes current window


    def close_self(self):
        self.close()

       


def update_display(userID):
    new_main = MainGuiDisplay(userID)
    new_main.show()


def restart_program():
    os.startfile(sys.argv[0])#restarts the file to completely reset the program
    sys.exit()


            
if __name__ == '__main__':
    app = QApplication(sys.argv)



    LoginUI = LoginDisplay()
    LoginUI.show()

    sys.exit(app.exec())      
    