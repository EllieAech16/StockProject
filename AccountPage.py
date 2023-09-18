
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




class AccountDetailsPage():
    ''' runs the account detail page '''
    
    def __init__(self, passedID):
        '''Initialises class variables'''
        self.current_user_ID = int(passedID)
        self.get_current_user_details()#calls function to get user details
        

    
    def get_current_user_details(self):
        '''retrieves all user information for page display '''
        
        try:
            conn = sqlite3.connect('NEA.db') #connect to database
            cursor = conn.cursor() # create a cursor to execute commands
            #print("Database connected") #shows message when connected to database


        except:
            print('Database connection error')


        get_user_details_sql = ('''SELECT FirstName, LastName, Email, Password FROM UserINFO
                                WHERE UserID = ? ''')
        
        get_user_details_data = self.current_user_ID 
        
        cursor.execute(get_user_details_sql, (get_user_details_data,))#executes SQL command

        user_details = cursor.fetchall()#retrieves all data relevant
        
        return user_details



    def change_first_name_db(self, current_first_name):
        '''Changes the users first name in database'''
        
        try:
            conn = sqlite3.connect('NEA.db') #connect to database
            cursor = conn.cursor() # create a cursor to execute commands
            #print("Database connected") #shows message when connected to database


        except:
            print('Database connection error')


        try:
            change_first_name_sql = ''' UPDATE UserInfo SET FirstName = ? WHERE UserID = ?;'''
            
            change_first_name_data = (str(current_first_name), int(self.current_user_ID))
            
            cursor.execute(change_first_name_sql, change_first_name_data)#executes SQL command
            
            conn.commit()
            
        except:
            print('failure')
            


    def change_last_name_db(self, current_last_name):
        '''Changes the users last name in database'''
    

        try:
            conn = sqlite3.connect('NEA.db') #connect to database
            cursor = conn.cursor() # create a cursor to execute commands
           # print("Database connected") #shows message when connected to database


        except:
            print('Database connection error')


        try:

            change_last_name_sql = ''' UPDATE UserInfo SET LastName = ? WHERE UserID = ?;'''
            
            change_last_name_data = (str(current_last_name), int(self.current_user_ID))
            
            cursor.execute(change_last_name_sql, change_last_name_data)#executes SQL command
            
            conn.commit()


        except:
            print('failure')



    def change_password_db(self, current_password):
        '''Changes the users last name in database'''

        try:
            conn = sqlite3.connect('NEA.db') #connect to database
            cursor = conn.cursor() # create a cursor to execute commands
            #print("Database connected") #shows message when connected to database


        except:
            print('Database connection error')

        #hashes password to store securely
        encoded_password = hashlib.md5(current_password.encode())#md5 hash function encodes 
        hashed_password = encoded_password.hexdigest()#converts the encoded hash to hex
        
        try:
            change_password_sql = ''' UPDATE UserInfo SET Password = ? WHERE UserID = ?;'''
            
            change_password_data = (str(hashed_password), int(self.current_user_ID))
            cursor.execute(change_password_sql, change_password_data)#executes SQL command
            conn.commit()


        except:
            print('failure')
            


    def change_email_db(self, current_email):
        '''Changes the users email in database'''
        current_email = current_email

        try:
            conn = sqlite3.connect('NEA.db') #connect to database
            cursor = conn.cursor() # create a cursor to execute commands
            #print("Database connected") #shows message when connected to database


        except:
            print('Database connection error')


        try:
            change_email_sql = ''' UPDATE UserInfo SET Email = ? WHERE UserID = ?;''' 
            
            change_email_data = (str(current_email), int(self.current_user_ID))
            cursor.execute(change_email_sql, change_email_data)#executes SQL command
            conn.commit()
            
        except:
            print('failure')
