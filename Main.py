import bs4 as bs
import datetime as dt
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
import requests
def sp500_tickers():    # gets all SP 500 symbols and writes it in a file
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        ticker = ticker[:-1]
        tickers.append(ticker)
    with open('sp500','wb') as f:
        #Pickle data is opaque, binary data
        pickle.dump(tickers, f)
    return tickers

def get_data_from_yahoo(reload_sp500=False):    # reads the symbol and gets basic
    # measurements for each one stoing it in a different file (for now it is changed to the first 25

    if reload_sp500:
        tickers = sp500_tickers()
    else:
        with open('sp500','rb') as f:
            tickers = pickle.load(f)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    start = dt.datetime(2000,1,1)
    end = dt.datetime(2016, 12, 31)
    for ticker in tickers[:20]:
        print(tickers)
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
            df = web.DataReader(ticker, 'yahoo', start, end)
            df.to_csv('stock_dfs/{}.csv'.format(ticker))
        else:
            print('Already have {}'.format(ticker))
#sp500_tickers()
get_data_from_yahoo()