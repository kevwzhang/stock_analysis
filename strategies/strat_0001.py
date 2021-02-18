import numpy as np
import pandas as pd
import yfinance as yf
import time
import sys, os

SIMULATE_COUNTER = 0 #used to simulate the day after 4:00pm eastern - remove all instances of this var when done

CASH = 25000.0
STOCK_PORTFOLIO = {}
STOCKS_WATCHLIST = ['SNAP', 'UBER', 'MSFT', 'AAPL', 'ABNB', 'PYPL', 'AMD', 'FB', 'TWTR', 'BABA', 'BAC', 'DIS', 'AAL', 'KO', 'SBUX', 'SQ', 'WMT', 'NKE']; STOCKS_WATCHLIST.sort()
MAX_STOCK_QTY = 2 #the max amount of shares I am willing to hold per stock
MAX_UNIT_PRICE = 100.0 #the max unit price I am willing to buy per share


def main():
    execute_tft_trading_strategy()


def execute_tft_trading_strategy():
    prev_stock_prices = init_stock_prices()
    while True:
#        print("loop")
        updated_stocks, curr_stock_prices = update_stock_prices(prev_stock_prices)
        if updated_stocks:
            print(curr_stock_prices)
            for ticker in updated_stocks:
                if curr_stock_prices[ticker] > prev_stock_prices[ticker]: #rising
                    #consider buying
                    if ticker not in STOCK_PORTFOLIO:
                        tft_buy(ticker, MAX_STOCK_QTY, curr_stock_prices[ticker]) #EXECUTE BUY
                    continue
                if curr_stock_prices[ticker] < prev_stock_prices[ticker]: #going down
                    #consider selling
                    if ticker in STOCK_PORTFOLIO:
                        tft_sell(ticker, MAX_STOCK_QTY, curr_stock_prices[ticker]) #EXECUTE SELL
                    continue

            print_portfolio_standings(curr_stock_prices)

        prev_stock_prices = curr_stock_prices

        time.sleep(10)


def tft_buy(ticker, quantity, price):
    #eventually replace with robinhood buy
    global CASH

    STOCK_PORTFOLIO[ticker] = (quantity, price)
    CASH -= quantity * price
    CASH = round(CASH, 2)
    print("Bought", quantity, "shares of", ticker, "at", price, "per share for a total of", quantity * price) #add time element?


def tft_sell(ticker, quantity, price):
    #eventually replace with robinhood sell
    global CASH

    del STOCK_PORTFOLIO[ticker]
    CASH += quantity * price
    CASH = round(CASH, 2)
    print("Sold", quantity, "shares of", ticker, "at", price, "per share for a total of", quantity * price) #add time element?


def print_portfolio_standings(curr_stock_data):
    from datetime import datetime
    print("\n")
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("====================================")
#    print("\n====================================")
    print("CURRENT POSITION")
    print("Stock\tShares\tValue\tBought At")
    total_worth = CASH
    for ticker in STOCKS_WATCHLIST:
        if ticker in STOCK_PORTFOLIO:
            shares = STOCK_PORTFOLIO[ticker][0]
            curr_val = round(curr_stock_data[ticker], 2)
            bought_price =STOCK_PORTFOLIO[ticker][1]
            total_worth += shares * curr_val
            total_worth = round(total_worth, 2)
            print(ticker + "\t" + str(shares) + "\t" + str(curr_val) + "\t" + str(bought_price))
    print("Cash:", CASH)
    print("Total Worth:", total_worth)
    print("====================================\n")


def init_stock_prices():
    stock_prices = {}
    for ticker in STOCKS_WATCHLIST:
        sys.stdout = open(os.devnull, 'w')
        yf_data = yf.download(tickers=ticker, period='1d', interval='1m').iloc[0] #beginning of day - NEED TO CHANGE TO BE RIGHT BEFORE STARTING
        sys.stdout = sys.__stdout__

        #if 'Adj Close' not in row
        stock_prices[ticker] = round(yf_data['Open'], 2)

    return stock_prices
    #check date to make sure it is always new?
    #make sure even with 100+ stocks the most recent values for all are gotten?


def update_stock_prices(stock_prices):
    global SIMULATE_COUNTER
    updated_stocks = []
    updated_stock_prices = {}
    for ticker in STOCKS_WATCHLIST:
        sys.stdout = open(os.devnull, 'w')
        if SIMULATE_COUNTER:
            yf_data = yf.download(tickers=ticker, period='1d', interval='1m').iloc[SIMULATE_COUNTER]
        else:
            yf_data = yf.download(tickers=ticker, period='1d', interval='1m').iloc[-1]
        sys.stdout = sys.__stdout__

        curr_val = round(yf_data['Open'], 2)
        #if 'Adj Close' not in row
        if curr_val == round(yf_data['Close'], 2): #is a live price and not a summary with case of hh:mm:00 summary data
            updated_stock_prices[ticker] = curr_val
            updated_stocks.append(ticker)
        else:
            updated_stock_prices[ticker] = stock_prices[ticker]

#    SIMULATE_COUNTER += 1

    return updated_stocks, updated_stock_prices
    #check date to make sure it is always new?
    #make sure even with 100+ stocks the most recent values for all are gotten?


if __name__ == "__main__":
    main()