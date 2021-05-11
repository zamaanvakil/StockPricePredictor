import numpy as np  
import pandas as pd  
from pandas_datareader import data as wb  
import matplotlib.pyplot as plt  
from scipy.stats import norm
import matplotlib.mlab as mlab
from scipy.stats import norm
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import shutil

class monte_carlo:
    
    def __init__(self, ticker):
        self.invalid_ticker = False
        data = pd.DataFrame()
        try:
            data[ticker] = wb.DataReader(ticker, data_source='yahoo', start='2018-1-1')['Adj Close']
        except:
            self.invalid_ticker = True
        
        if not self.invalid_ticker:
            if os.path.exists('static/images/output'):
                shutil.rmtree('static/images/output')
            os.mkdir('static/images/output')
            log_returns = np.log(1 + data.pct_change())
            self.ticker = ticker
            self.data = data
            self.log_returns = log_returns

            self.name = str(int(time.time()))

            self.currency, self.company_name, self.se_name = self.currency_scrapper(ticker)
    
    def plot_historical_data(self):
        if self.invalid_ticker:
            return -1,-1
        data = self.data
        ticker = self.ticker
        log_returns = self.log_returns
        name = self.name
    
        data.plot(figsize=(10, 6),color='red');
        plt.ylabel('Price('+self.currency+')')
        plt.title('Historical Price of '+str(ticker)+' Stock',fontsize=18, fontweight='bold')
        name1 = 'static/images/output/'+name+'_1.png'
        plt.savefig(name1)

        log_returns.plot(figsize = (10, 6))
        plt.ylabel("Log Returns")
        plt.title('Historical Log Returns',fontsize=18, fontweight='bold')
        name2 = 'static/images/output/'+name+'_2.png'
        plt.savefig(name2)

        print("NAME1: "+name1)
        return name1[7:],name2[7:]
    
        
    def brownian_motion(self,sim_days,sim_num,show_hist = True):
        if self.invalid_ticker:
            return -1,-1,-1,-1
        data = self.data
        log_returns = self.log_returns
        ticker = self.ticker
        name = self.name
        
        u = log_returns.mean()
        var = log_returns.var()
        
        drift = u - (0.5 * var)        
        daily_volatility = log_returns.std()
    
        shock = drift.values + daily_volatility.values*norm.ppf(np.random.rand(sim_days, sim_num))
    
        daily_returns = np.exp(shock)
        
        last_price = data.iloc[-1]
        
        price_list = np.zeros_like(daily_returns)        
        price_list[0] = last_price
        
        for t in range(1, sim_days):
            price_list[t] = price_list[t - 1] * daily_returns[t]
            
        plt.figure(figsize=(10,6))
        plt.plot(price_list)
        plt.title(str(sim_days)+' Days Monte Carlo Simulation for '+ str(ticker),fontsize=18,fontweight='bold')
        plt.xlabel('Days')
        plt.ylabel('Price ('+self.currency+')')
        #plt.show()
        name3 = 'static/images/output/'+name+'_3.png'
        plt.savefig(name3)

        price_array = price_list[-1]
        start = price_array.mean() - norm.ppf(0.56)*np.std(price_array)
        end = price_array.mean() + norm.ppf(0.56)*np.std(price_array)
    
        retval_str = "Probability price is between "+self.currency+' '+ str(round(start,2)) +" and "+self.currency+' '+ str(round(end,2)) +": " + "{0:.2f}%".format((float(len(price_array[(price_array > start) & (price_array < end)])) / float(len(price_array)) * 100))
        self.price_array = price_array
        most_prob_price = price_array[(price_array > start) & (price_array < end)].mean()
        retval_str1 = "Most probable price is "+self.currency+' '+ str(round(most_prob_price,2))

        name4 = 0

        if show_hist:
            name4 = self.histogram(price_list[-1],last_price,most_prob_price)

        return retval_str,retval_str1,name3[7:],name4[7:]
            
            
    def histogram(self,ser,last_price,most_prob_price):
        name = self.name
        x = ser
        mu = ser.mean()
        sigma = ser.std()
        
        num_bins = 20
        # the histogram of the data
        plt.figure(figsize=(10,6))
        n, bins, patches = plt.hist(x, num_bins, rwidth=0.9, density=1, facecolor='green', alpha=0.6)
             
        # add a 'best fit' line
        #y = mlab.normpdf(bins, mu, sigma)
        y = norm.pdf(bins, mu, sigma)
        plt.plot(bins, y, 'r--')
        plt.xlabel('Price ('+self.currency+')')
        plt.ylabel('Probability')
        plt.title(r'Histogram of Simulated Stock Prices', fontsize=18, fontweight='bold')
        plt.axvline(x=last_price.values, color='black', linestyle='--', label = 'Current Stock Price: '+str(round(last_price.values[0],2)))
        plt.axvline(x=most_prob_price, color='blue', linestyle='--', label = 'Predicted Price: '+str(round(most_prob_price,2)))
        plt.legend(loc="upper right")
        # Tweak spacing to prevent clipping of ylabel
        plt.subplots_adjust(left=0.15)
        
        #plt.show()
        name4 = 'static/images/output/'+name+'_4.png'
        plt.savefig(name4) 

        return name4

    def currency_scrapper(self,ticker):
        url = "https://in.finance.yahoo.com/quote/"+ticker
        html = urlopen(url)
        soup = BeautifulSoup(html, 'lxml')
        tag_data = soup.find_all('span')
        tag_data = tag_data[16]
        curr_str = tag_data.text
        curr_str = curr_str.split()
        print(curr_str)
            
        stock_ex_nm = curr_str[0]   #stock exchange name
        curr_str = curr_str[-1]     #currency symbol
            
        tag_data = soup.find_all('h1')
        tag_data = tag_data[0]
        comp_nm = tag_data.text
        comp_nm = comp_nm.split('-')[-1]
        comp_nm = comp_nm.strip()   #company name
        
        return curr_str, comp_nm, stock_ex_nm 
        