import requests
import csv
import sys
import sqlite3
import _sqlite3
import datetime
from bs4 import BeautifulSoup
#import libraries


class StockData():
    '''Scrapes, calculates and appends all stock data to databases'''
    
    def __init__(self):
        self.refresh_names = False
        self.symbol_list = []
        self.name_list = []
        self.price_list = []
        self.price_change_list = []
        self.price_change_percent_list = []
        self.contents_list = []
        self.volume_list = []
        self.temp = []
        self.temp_2 = []



    def get_stock_info(self):
        '''Scrapes the name, symbol, price and price change of each stock in the FTSE 100'''
        self.contents_list = []
        self.symbol_list = []
        self.name_list = []
        self.price_list = []
        self.price_change_list = []
        self.price_change_percent_list = []


        HLURL = "https://www.hl.co.uk/shares/stock-market-summary/ftse-100" #specified url


        try: 
            URL_req = requests.get(HLURL)#sends a request to the server

            req_content = BeautifulSoup(URL_req.content, 'html5lib')#requests all html from the target url

            URL_text = req_content.get_text()#retrieves all displayed text from the html


        except:
            #if the request does not succesfully go through, an exception is returned. 
            print('Cannot connect to server')
            

        
        split_URL_txt = URL_text.split()#splits retrieved text into list

        start_scrape = split_URL_txt.index('change')#sets start of scrape for retrieved text
        
        end_scrape = split_URL_txt.index('FAQs')#sets end of scrape

        scrape_data = split_URL_txt[start_scrape+1:end_scrape]#splits the relevant details into another list


        for item in scrape_data:
            if item == 'Deal': #Deal is displayed after the data of each stock
                
                self.contents_list.append(self.temp)#if deal is the current item, the current list of stock data will be appended to the contents
                
                self.temp = []


            else:
                self.temp.append(item)

        
        index_1 = 1
        
        self.temp_2 = []

        #for loop sorts the contents of each stock into categorised lists
        #able to index each list as the positions of each piece of data rarely differ
        
        for index_list in self.contents_list:
            index_1 = 1
            
            self.price_list.append(index_list[-3])
            
            self.price_change_list.append(index_list[-2])
            
            self.price_change_percent_list.append(index_list[-1])
            
            for item in index_list:
                if index_1 == 1:
                    
                    self.symbol_list.append(item)
                    
                    index_1 += 1
                    
                elif index_1 == 2 :
                    self.temp_2.append(item)
                    
                    index_1 += 1
                    
                elif index_1 >= 3:
                    if item.isalpha() == True: #checks if current item is all letters
                        
                        self.temp_2.append(item)
                        
                        index_1 += 1
                        
                    elif (item[0].isalpha() and item[-1].isalpha()) == True:
                        self.temp_2.append(item)
                        
                        index_1 += 1

                    
                    else:
                        pass

                    
            self.name_list.append(" ".join(self.temp_2))
            
            self.temp_2 = []

            


    def get_stock_volume(self):
        '''Scrapes Stock Volume '''
        
        self.volume_list = []
        
        SCURL = "https://www.sharecast.com/index/FTSE_100" #specified url

        URL_req = requests.get(SCURL)#sends a request to the

        req_content = BeautifulSoup(URL_req.content, 'html5lib')#requests all html from the target url

        URL_text = req_content.get_text()#retrieves all displayed text from the html

        split_URL_txt = URL_text.split()#splits retrieved text into list

        #print(split_URL_txt)

        start_vol_scrape = split_URL_txt.index('Time')#sets start of scrape for retrieved text

        
        end_vol_scrape = split_URL_txt.index('About')#sets end of scrape

        vol_scrape_data = split_URL_txt[start_vol_scrape+1:end_vol_scrape]#splits the relevant details into another list

        index_4 = 1
        
        self.volume_list = []


        for vol_item in vol_scrape_data:
            if ('%' in str(vol_item)): #if volume present 
                self.volume_list.append(vol_scrape_data[index_4])
                
                index_4 += 1

                
            else:
                index_4 += 1

       ########### self.volume_list.insert(84, '0')


        

    def append_names_symbols(self):
        '''Appends updated names and symbols to a database '''
     
        conn = sqlite3.connect('NEA.db', isolation_level=None ) #connect to database
        
        cursor = conn.cursor() # create a cursor to execute commands
        
        #print("Database connected") #shows message when connected to database

        
        for symbol in self.symbol_list:
            index = self.symbol_list.index(symbol)
        
            insert_stockdata_sql = '''INSERT INTO StockIdentification(StockName, StockSymbol) VALUES(?,?); '''
        
            insert_stockdata = (self.name_list[index], symbol)
    
            cursor.execute(insert_stockdata_sql, (insert_stockdata))
        
            conn.commit()
           

        #print('sucess')
        
        conn.commit()


        

    def append_price_vol(self):
        '''Appends Stock Price and Volume to a database '''
        
        conn = sqlite3.connect('NEA.db', isolation_level=None ) #connect to database
        
        cursor = conn.cursor() # create a cursor to execute commands
        
        #print("Database connected") #shows message when connected to database
        
        index_5 = 0


        for symbol in self.symbol_list:
            #Gets information for insertion to databse
            get_stockID_sql = '''SELECT StockID FROM StockIdentification WHERE Stocksymbol = ? ; '''#gets stockID
            
            cursor.execute(get_stockID_sql, (symbol,))
            
            current_stockID = cursor.fetchmany(1)
            
            conn.commit()

            insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")#gets current time


            #insert stock price data into stock price table
            insert_price_sql = '''INSERT INTO StockPrice(StockID, Price, PriceDateTime) VALUES (?,?,?);'''#insert price data into stock price table
            
            stockprice = self.price_list[index_5]
            
            intstockprice = stockprice.replace("," , "")#formatting
            
            insert_price_data = (current_stockID[0][0], float(intstockprice), str(insert_time))
            
            cursor.execute(insert_price_sql, (insert_price_data))
            
            conn.commit()

          
            #insert volume data into stock volume table
            insert_volume_sql = '''INSERT INTO StockVolume(StockID, Volume, VolumeDateTime) VALUES (?,?,?); '''
 
            stockvolume = self.volume_list[index_5]
            
            intstockvolume = stockvolume.replace("," , "")

            insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            insert_volume_data = (current_stockID[0][0], int(intstockvolume), str(insert_time))

            cursor.execute(insert_volume_sql, (insert_volume_data))
            
            conn.commit()

        
            #inserts price change and percentage change into database
            insert_change_sql = """INSERT INTO StockChange(StockID, Change, PercentChange, ChangeDateTime) VALUES (?,?,?,?); """
            
            stock_change = self.price_change_list[index_5]
            
            stock_percent_change = self.price_change_percent_list[index_5]
            
            insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            insert_change_data = (current_stockID[0][0]), stock_change ,stock_percent_change, str(insert_time)
            
            cursor.execute(insert_change_sql, (insert_change_data))
            
            conn.commit()
            
            index_5 += 1
            


                    
    def check_names_symbols(self):
        '''Checks all stock names and symbols to see if upto date '''
        
       #get info from previous return
        conn = sqlite3.connect('NEA.db') #connect to database
        
        cursor = conn.cursor() # create a cursor to execute commands
        
        #print("Database connected") #shows message when connected to database


        #retrieve stock name
        cursor.execute('''SELECT StockName FROM StockIdentification ORDER BY StockID ASC;''')
        
        retrieved_name = cursor.fetchall()
        
        conn.commit()


        #retrieve stock symbol
        cursor.execute('''SELECT StockSymbol FROM StockIdentification ORDER BY StockID ASC ;''')
 
        retrieved_symbol = cursor.fetchall()

        conn.commit()


        #compares database information with retrieved information to see if it needs to be updated
        self.refresh_names = False
        
        index_2 = 0


        if retrieved_name == [] or retrieved_symbol == []: #if lists empty sets refresh to true
            self.refresh_names = True

            
        else:
            for name in self.name_list:
                
                if name != str(retrieved_name[index_2][0]):#if difference found refresh will be set to true
                    
                    self.refresh_names = True
                    
                    break

                
                else:
                    index_2 += 1
                

            index_3 = 0
            
            for symbol in self.symbol_list:
                if symbol != retrieved_symbol[index_3][0]:#if difference found refresh will be set to true
                    
                    self.refresh_names = True
                    
                    break

                
                else:
                    index_3 += 1
            
        return self.refresh_names




    def get_all_stockIDs(self):
        ''' gets a list of all stockIDs'''

        conn = sqlite3.connect('NEA.db', isolation_level=None ) #connect to database
        
        cursor = conn.cursor() # create a cursor to execute commands
        
        #print("Database connected") #shows message when connected to database


        #gets all stockIDs
        get_stockID_sql = """SELECT StockID FROM StockIdentification; """
        
        cursor.execute(get_stockID_sql)
        
        all_stockIDs = cursor.fetchall()
        
        return all_stockIDs




    def get_user_stocks(self, userID):
        '''Retrieves all data from a users account'''

        userID = userID
        
        conn = sqlite3.connect('NEA.db', isolation_level=None ) #connect to database
        
        cursor = conn.cursor() # create a cursor to execute commands
        
        #print("Database connected") #shows message when connected to database

        get_user_stocks_info_sql = """SELECT StockIdentification.StockName, StockIdentification.StockSymbol,
                                    UserStocks.StockID  FROM StockIdentification
                                    INNER JOIN UserStocks ON StockIdentification.StockID = UserStocks.StockID
                                    WHERE UserStocks.UserID = ? ;"""

        cursor.execute(get_user_stocks_info_sql, (userID,))
        
        user_stock_info = cursor.fetchall()
        
        conn.commit()


        self.user_stock_name_list = []
        
        self.user_stock_symbol_list = []
        
        self.user_stockID_list = []


        #creates and sorts the stockID, name and symbol into lists
        for stock in user_stock_info:
            self.user_stock_name_list.append(stock[0])
            
            self.user_stock_symbol_list.append(stock[1])
            
            self.user_stockID_list.append(stock[2])
        

        
        self.user_stock_price_list = []
        

        #retrieves prices for the users stocks
        for ID in self.user_stockID_list:
            get_user_stock_price_sql = """SELECT Price from StockPrice WHERE StockID = ? ORDER BY PriceDatetime DESC LIMIT 1 ;"""
            
            cursor.execute(get_user_stock_price_sql, (ID,))
            
            temp_append = cursor.fetchmany(1)
            
            self.user_stock_price_list.append(temp_append)
            
            conn.commit()


            

    def get_user_stockID(self):
        return self.user_stockID_list
    

    def get_user_stock_price(self):
        return self.user_stock_price_list
    

    def get_user_stock_name(self):
        return self.user_stock_name_list
    

    def get_user_stock_symbol(self):
        return self.user_stock_symbol_list
    
        
    def get_price_list(self):
        return self.price_list
    

    def get_name_list(self):
        return self.name_list
    

    def get_symbol_list(self):
        return self.symbol_list
    

    def get_price_change_list(self):
        return self.price_change_list
    

    def get_price_change_percent_list(self):
        return self.price_change_percent_list
        
        
        

        
    

        


    


