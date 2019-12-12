import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
from collections import Counter
from sklearn import svm, neighbors
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split
import scraper

style.use('ggplot')
def save_sp500_tickers():
    URL_BASE = 'https://www.investopedia.com/articles/investing/053116/10-largest-holdings-sp-500-aaplamznfb.asp'
    stock_scrape = scraper.UrlScraper(URL_BASE)
    tickers = []
    for x in range(15):
        ticket = stock_scrape.pull_from_to(
            'data-component="link" data-source="inlineLink" data-type="externalLink" data-ordinal="1" rel="nofollow">',
            '</a>')
        tickers.append(ticket.replace(".","-"))
    with open('sp500tickers.pickle', 'wb') as f:
        # Pickle data is opaque, binary data
        pickle.dump(tickers, f)
    print(tickers)
    return tickers


# save_sp500_tickers()
def get_data_from_yahoo(reload_sp500=False):
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open("sp500tickers.pickle", "rb") as f:
            tickers = pickle.load(f)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    start = dt.datetime(2018, 8, 5)
    end = dt.datetime(2019, 9, 5)
    for ticket in tickers:
        if not os.path.exists('stock_dfs/{}.csv'.format(ticket)):
            print('Getting Ticket: {}'.format(ticket))
            df = web.DataReader(ticket, 'yahoo', start, end)
            df.to_csv('stock_dfs/{}.csv'.format(ticket))
        else:
            print('Already have {}'.format(ticket))


def compile_data():
    with open("sp500tickers.pickle", "rb") as f:
        tickers = pickle.load(f)
    main_df = pd.DataFrame()
    for count, ticker in enumerate(tickers):
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        df.set_index('Date', inplace=True)
        df.rename(columns={'Adj Close': ticker}, inplace=True)
        df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')
    print("\n\nAdjusted Close of All tickets \n",main_df.head())
    main_df.to_csv('sp500_joined_closes.csv')

def visualize_data():
    df = pd.read_csv('sp500_joined_closes.csv')
    df_corr = df.corr()
    print("\n\nCorrelation Co-efficient of All Stocks\n", df_corr.head())
    df_corr.to_csv('sp500corr.csv')
    data1 = df_corr.values
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1,1,1) # of rows, # of columns, position of graph you are plotting
    heatmap1 = ax1.pcolor(data1, cmap=plt.cm.RdYlBu)
    fig1.colorbar(heatmap1)
    ax1.set_xticks(np.arange(data1.shape[0]) + 0.5, minor=False)
    ax1.set_yticks(np.arange(data1.shape[1]) + 0.5, minor=False)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax1.set_xticklabels(column_labels)
    ax1.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap1.set_clim(-1, 1)
    plt.tight_layout()
    plt.show()

def process_data_for_labels(ticker):
    hm_days = 7
    df = pd.read_csv('sp500_joined_closes.csv', index_col=0)
    tickers = df.columns.values.tolist()
    df.fillna(0, inplace=True)

    for i in range(1,hm_days+1):
        df['{}_{}d'.format(ticker,i)] = (df[ticker].shift(-i) - df[ticker]) / df[ticker]
    df.fillna(0, inplace=True)
    return tickers, df

def buy_sell_hold(*args):
    cols = [c for c in args]
    requirement = 0.02
    for col in cols:
        if col > requirement:
            return 1
        if col < -requirement:
            return -1
    return 0    # if the return is above 2% then return 1, -1 for less than, and 0 for anything in between

def extract_featuresets(ticker):
    tickers, df = process_data_for_labels(ticker)

    df['{}_target'.format(ticker)] = list(map( buy_sell_hold,
                                               df['{}_1d'.format(ticker)],
                                               df['{}_2d'.format(ticker)],
                                               df['{}_3d'.format(ticker)],
                                               df['{}_4d'.format(ticker)],
                                               df['{}_5d'.format(ticker)],
                                               df['{}_6d'.format(ticker)],
                                               df['{}_7d'.format(ticker)]))
    vals = df['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]
    print('Data spread:', Counter(str_vals))

    df.fillna(0, inplace=True)
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(inplace=True)

    df_vals = df[[ticker for ticker in tickers]].pct_change()
    df_vals = df_vals.replace([np.inf, -np.inf], 0)
    df_vals.fillna(0, inplace=True)

    X = df_vals.values
    y = df['{}_target'.format(ticker)].values
    print(df)
    return X, y, df

def do_ml(ticker):
    X, y, df = extract_featuresets(ticker)
    # y is the target
    # X is the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

    clf = VotingClassifier([('lsvc', svm.LinearSVC()),
                            ('knn', neighbors.KNeighborsClassifier()),
                            ('rfor', RandomForestClassifier())])

    clf.fit(X_train, y_train)
    confidence = clf.score(X_test, y_test)
    print('accuracy:', confidence)
    predictions = clf.predict(X_test)
    print('predicted class counts:', Counter(predictions))
    print()
    print()
    return confidence


# examples of running:
save_sp500_tickers()
get_data_from_yahoo()
compile_data()
visualize_data()
do_ml('MSFT')

# 1. Use Web Scriper for top 20 most traded stocks in S&P 500
# 2. Use Yahoo Data Reader to get basic stats for each stock
# 3. The stocks are stored in csv to avoid scraping/reloading every time
# 4. Create a combined CSV for all adjusted-close for every stock
# 5. Utilize Panda Dataframe to create correlation heatmap for the combined CSV
# 6.
