import yfinance as yf
import numpy as np 
import datetime
from datetime import *
from dateutil.relativedelta import *

import sys
import sqlite3
import _sqlite3

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.uic import *
from PyQt5.QtWidgets import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from WebScraping import StockData
###Imports libraries###




class StockButton():
    '''creates a button object with unique data'''


    def __init__(self, stockID, userID, mainguiself):
        
        self.stockID = stockID
        
        self.userID = userID
        
        self.main_gui_obj = mainguiself
        #defines variables passed

    
        self.viewstock_btn = QPushButton('View Stock')#creates button
        
        self.viewstock_btn.clicked.connect(self.view_stock_page)#when clicked, calls stock page function

        


    def view_stock_page(self):
        '''creates a stock page object based off of buttons unique data  '''
        self.stockpage_obj = StockPage(self.stockID, self.userID, self.main_gui_obj) #creates object


        

class StockPage(QWidget):
    '''Creates and manages stock page gui '''
    


    def __init__(self, stockID, userID, mainguiself):
        '''initialises variables'''
        self.stockID = stockID
        
        self.userID = userID
        
        self.main_gui_obj = mainguiself
        
        self.stock_data_obj = StockData()


        super().__init__()

        self.main_gui_obj.close_self()
    
        self.retrieve_current_stock_info()
     
        self.setWindowTitle(self.stock_name)
        self.resize(1200,800)
       
        self.init_UI()
        
        self.setLayout(self.grid_layout)
        self.show()
    


    def init_UI(self):
        ''''initialises each element of the page on a window '''
        
        self.grid_layout = QGridLayout() # calls layout

        #Creates label for stock name and stock symbol#
        self.stock_name_lbl = QLabel(self.stock_name)#Creaes a label with the stocks name
        self.stock_name_lbl.setFont(QFont('Arial', 18))#Sets labels font and size
        self.grid_layout.addWidget(self.stock_name_lbl, 0, 1)#Places label on grid 

        self.stock_symbol_lbl = QLabel(self.stock_symbol)
        self.stock_symbol_lbl.setFont(QFont('Arial', 14))
        self.grid_layout.addWidget(self.stock_symbol_lbl, 0, 2)


        #Creates and displays labels for stock finance information#
        self.price_label_lbl = QLabel('Price')
        self.price_label_lbl.setFont(QFont('Arial', 14))
        self.grid_layout.addWidget(self.price_label_lbl, 1, 1)

        self.stock_price_lbl = QLabel(str(self.stock_price) + 'p')
        self.stock_price_lbl.setFont(QFont('Arial', 14))
        self.grid_layout.addWidget(self.stock_price_lbl, 1, 2)

        self.volume_label_lbl = QLabel('Volume')
        self.volume_label_lbl.setFont(QFont('Arial', 14))
        self.grid_layout.addWidget(self.volume_label_lbl, 2, 1)
        self.stock_volume_lbl = QLabel(str(self.stock_volume))
        self.stock_volume_lbl.setFont(QFont('Arial', 14))
        self.grid_layout.addWidget(self.stock_volume_lbl, 2, 2)

        self.stock_change_label_lbl = QLabel('Day Change')
        self.stock_change_label_lbl.setFont(QFont('Arial', 14))
        self.grid_layout.addWidget(self.stock_change_label_lbl, 3, 1)
        self.stock_change_lbl = QLabel(str(self.stock_change))
        self.stock_change_lbl.setFont(QFont('Arial', 14))
        self.grid_layout.addWidget(self.stock_change_lbl, 4, 1)
        
        self.stock_percent_lbl = QLabel(self.stock_change_percent)
        self.stock_percent_lbl.setFont(QFont('Arial', 14))
        self.grid_layout.addWidget(self.stock_percent_lbl, 4, 2)


        #Creates buttons to manage watchlist#
        add_to_watchlist_btn = QPushButton('Add To Watchlist')#Creates a button
        add_to_watchlist_btn.clicked.connect(self.add_stock_to_watchlist)#connects to function
        self.grid_layout.addWidget(add_to_watchlist_btn, 0,3)#add button to layout 

        remove_from_watchlist_btn = QPushButton('Remove from Watchlist')
        remove_from_watchlist_btn.clicked.connect(self.remove_stock_from_watchlist)
        self.grid_layout.addWidget(remove_from_watchlist_btn, 1,3)


        #Creates button to navigate pages# 
        go_to_main_btn = QPushButton('Back')
        go_to_main_btn.clicked.connect(self.go_to_main)
        self.grid_layout.addWidget(go_to_main_btn, 6,3)

        
        #cretes graph and plots#
        self.figure = plt.figure(figsize = (70,20))#creates an object of a figure and assigns size
        self.canvas = FigureCanvas(self.figure)#creates canvas for figure object
        self.grid_layout.addWidget(self.canvas, 2,3)#adds canvas to layout
        self.plot()#calls function to plot graph


        #create a slider
        self.timeframe_sldr = QSlider(Qt.Horizontal, self)#sets slider
        self.timeframe_sldr.setGeometry(30,40,200,30)#sets size
        self.timeframe_sldr.setRange(0,4)#sets range of ticks
        self.timeframe_sldr.setTickInterval(1)#sets interval of ticks
        self.timeframe_sldr.setTickPosition(QSlider.TicksBelow)#sets ticks to show below
        self.timeframe_sldr.valueChanged.connect(self.calculate_timeframe)#connects the slider
        self.grid_layout.addWidget(self.timeframe_sldr, 4,3)#adds widget to layout


        #create default time label for slider
        self.timeframe_lbl = QLabel('1 year')
        self.grid_layout.addWidget(self.timeframe_lbl, 5,3)

        
        #create update button for graph
        self.update_btn = QPushButton('Update')
        self.update_btn.clicked.connect(self.plot)
        self.grid_layout.addWidget(self.update_btn, 3,4)


        

    def calculate_timeframe(self):
        '''Calculates the timeframe for displaying and retrieving'''
        
        try:
            if self.timeframe_sldr.value() == 0:
                #1 year
                self.timeframe_lbl.setText('1 Year')
                self.start_scrape_date = date.today() - relativedelta(years=1)
                self.scrapeinterval = "1d"

                
            elif self.timeframe_sldr.value() == 1:
                #6 months
                self.timeframe_lbl.setText('6 Months')
                self.start_scrape_date = date.today() - relativedelta(months = 6)
                self.scrapeinterval = "1d"


            elif self.timeframe_sldr.value() == 2:
                #1 month
                self.timeframe_lbl.setText('1 Month')
                self.start_scrape_date = date.today() - relativedelta(months = 1)
                self.scrapeinterval = "1d"


            elif self.timeframe_sldr.value() == 3:
                #1 week
                self.timeframe_lbl.setText('1 Week')
                self.start_scrape_date = date.today() - relativedelta(weeks = 1)
                self.scrapeinterval = "1h"


            elif self.timeframe_sldr.value() == 4:
                #1 day
                self.timeframe_lbl.setText('1 Day')
                self.start_scrape_date = date.today() - relativedelta(days = 1)
                self.scrapeinterval = "30m"


            else:
                #sets default 
                self.timeframe_lbl.setText('1 Year')
                self.start_scrape_date = date.today() - relativedelta(years=1)
                self.scrapeinterval = "15m"


        except:
            #sets default
            self.start_scrape_date = date.today() - relativedelta(years=1)
            self.scrapeinterval = "1d"

            
            

    def retrieve_current_stock_info(self):
        '''retrieves all information for the specific stock passed '''
        
        try:
            conn = sqlite3.connect('NEA.db') #connect to database
            cursor = conn.cursor() # create a cursor to execute commands
            #print("Database connected")

        except:
            print('Database connection error')


        #retrieves stocks name and symbol#
        retrieve_name_symbol_sql = """ SELECT StockName, StockSymbol FROM StockIdentification WHERE StockID = ?; """ #create SQL statement
        
        cursor.execute(retrieve_name_symbol_sql, (self.stockID,))#executes sql statement with data
        
        stockname_symbol = cursor.fetchmany(1)#asigns to fetched records to variable
        
        conn.commit()#commits connection


        #retrieves stock volume#
        retrieve_price_volume_sql = """ SELECT StockPrice.Price, StockVolume.Volume FROM StockPrice
                                        INNER JOIN StockVolume ON StockPrice.StockID = StockVolume.StockID
                                        WHERE StockPrice.StockID = ? AND StockPrice.StockID = ?
                                        ORDER BY StockPrice.PriceDateTime DESC, StockVolume.VolumeDateTime DESC
                                        LIMIT 1;"""
                                        
        retrieve_price_vol_data = (self.stockID, self.stockID)
        
        cursor.execute(retrieve_price_volume_sql, retrieve_price_vol_data)
        
        stock_price_vol = cursor.fetchall()
        
        conn.commit()


        #retrieves stock change data#
        retrieve_stock_changes_sql = """SELECT Change, PercentChange FROM StockChange WHERE StockID = ?
                                        ORDER BY ChangeDateTime DESC LIMIT 1; """
        
        cursor.execute(retrieve_stock_changes_sql, (self.stockID,))
        
        stock_price_change = cursor.fetchall()
        
        conn.commit()


        #asigns key variables
        self.stock_name = stockname_symbol[0][0]
        self.stock_symbol = stockname_symbol[0][1]
        self.stock_price = stock_price_vol[0][0]
        self.stock_volume = stock_price_vol[0][1]
        self.stock_change = stock_price_change[0][0]
        self.stock_change_percent = stock_price_change[0][1]


                
    def plot(self):
        ''' retrieves info and plots on graph'''

        try:#trys to clear existing graph
            plt.cla()
            
            plt.clf()


        except:
            pass
            
        
        self.calculate_timeframe()
    
        end_scrape_date = date.today()#ends scrape for current


        if '.' in self.stock_symbol: 
            historical_stock_data = yf.download(self.stock_symbol + 'L', start = self.start_scrape_date, end = end_scrape_date, interval= str(self.scrapeinterval))
            #ensures correct symbol is used in the URL, as all stocks in the ftse have .L after
   
            plt.title(" Opening Prices from " + str(self.start_scrape_date) + " to " + str(end_scrape_date))#sets title of figure
            

        else:
            historical_stock_data = yf.download(self.stock_symbol + '.L', start = self.start_scrape_date, end = end_scrape_date, interval = str(self.scrapeinterval))
   
            plt.title(" Opening Prices from " + str(self.start_scrape_date) + " to " + str(end_scrape_date))
            

        price_figure = historical_stock_data['Open'] #creates figure from correct opening data
        
        plt.plot(price_figure)#plots data on figure object
        
        self.canvas.draw()#draws figure on canvas
        

        
        
    def remove_stock_from_watchlist(self):
        '''removes selected stock from users watchlist '''
        
        try:
            conn = sqlite3.connect('NEA.db') #connect to database
            
            cursor = conn.cursor() # create a cursor to execute commands
            
            #print("Database connected")


        except:
            print('Database connection error')


        try:
            check_to_delete_sql = ("""SELECT * FROM UserStocks WHERE StockID = ? AND UserID = ? ; """)
            
            check_to_delete_data = (str(self.stockID), str(self.userID))
            
            cursor.execute(check_to_delete_sql, check_to_delete_data)
            
            check_to_delete = cursor.fetchall()

            
            if check_to_delete == []:
                QMessageBox.about(self, "Error", "Unable to remove")


            else:
                remove_user_stock_sql = """ DELETE FROM UserStocks WHERE StockID = ? AND UserID =? ; """
                
                remove_user_stock_data = (str(self.stockID), str(self.userID))
                
                cursor.execute(remove_user_stock_sql, remove_user_stock_data)
                
                conn.commit()
                
                self.go_to_main()

            
        except:
            QMessageBox.about(self, "Error", "Unable to remove")
            



    def add_stock_to_watchlist(self):
        '''adds a stock to the users watchlist '''
        
        try:
            conn = sqlite3.connect('NEA.db') #connect to database
            
            cursor = conn.cursor() # create a cursor to execute commands
            
            #print("Database connected")


        except:
            print('Database connection error')


        try:
            insert_watchlist_stock_sql = """INSERT INTO UserStocks(UserID, StockID)
                                            VALUES(?, ?);""" #sets SQL command """
            
            insert_watchlist_stock_data = (str(self.userID), str(self.stockID))
            
            cursor.execute(insert_watchlist_stock_sql, insert_watchlist_stock_data)
            
            conn.commit()
            
            self.go_to_main()
            
            
        except:
            QMessageBox.about(self, "Error", "Unable to add")


    def go_to_main(self):
        self.main_gui_obj.show()
        self.close()





