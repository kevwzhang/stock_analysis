import argparse
import datetime
import importlib
import pandas as pd
import pytz
import time
import yahoo_fin.stock_info

DATASET_FILEPATH = "datasets/"
STRATEGIES_MODULE_PREFIX = "strategies."

STOCKS_WATCHLIST = ['SNAP', 'UBER', 'MSFT', 'ABNB', 'AAPL']; STOCKS_WATCHLIST.sort()

CASH = 25000.0 #minimum amount of cash needed to day trade regularly
STOCK_PORTFOLIO = {}

TIME_DELAY_FLAG = True #True to simulate the time delays when retrieving stock prices, False to run simulation instantly

def main():
    """
    Runner for different stock buying/selling strategies
    """
    args = init_parser()

    strategy = importlib.import_module(STRATEGIES_MODULE_PREFIX + args.strategy)

    #simulate live prices
    if args.test == "simlive":
        print("Simulating Live Stock Price Quotes")

        sim_live_df = load_sim_live_dataset(DATASET_FILEPATH + args.datafile)

        for index, row in sim_live_df.iterrows():

            if TIME_DELAY_FLAG:
                if index == 0:
                    prev_time = row['Datetime'][:-6]
                curr_time = row['Datetime'][:-6]
                time_delay = datetime.datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(prev_time, "%Y-%m-%d %H:%M:%S")
                time.sleep(time_delay.total_seconds())
                prev_time = curr_time

            curr_stock_prices = get_simulated_live_data(row)
            pretty_print_stock_prices(curr_stock_prices)
            trades = strategy.main(curr_stock_prices)
            if trades["Sell"]:
                sell(trades["Sell"], curr_stock_prices)
            if trades["Buy"]:
                buy(trades["Buy"], curr_stock_prices)
            pretty_print_porfolio_standing(curr_stock_prices)

        print("\nFINAL RESULTS:\n")
        pretty_print_porfolio_standing(curr_stock_prices)

    #use real-time prices
    elif args.test == "realtime":
        print("Using Real-time Stock Price Quotes")

        if not during_trading_hours():
            print("Not currently normal trading hours")
            return

        while during_trading_hours():
            curr_stock_prices = get_live_data()
            if not curr_stock_prices:
                continue #failed to get prices for some reason, start loop over and try again
            pretty_print_stock_prices(curr_stock_prices)
            trades = strategy.main(curr_stock_prices)
            if trades["Sell"]:
                sell(trades["Sell"], curr_stock_prices)
            if trades["Buy"]:
                buy(trades["Buy"], curr_stock_prices)
            pretty_print_porfolio_standing(curr_stock_prices)

        print("\nFINAL RESULTS:\n")
        pretty_print_porfolio_standing(curr_stock_prices)


def init_parser():
    """
    Parses user input to determine which strategy to test and which dataset to test on
    Example command use: python3 strat_tester.py strat_0001 simlive 2021-02-18_live.csv
    arg strategy: name of the py file containing the trading strategy
    arg test: command that determines whether to use old, recorded live data or to use real-time stock prices
    arg datafile: name of the csv file containing the live prices data
    return <class 'argparse.Namespace'> args: the argument values the user provides
    """
    parser = argparse.ArgumentParser(description='Used to test run different stock stategies')
    parser.add_argument("strategy")
    parser.add_argument("test")
    parser.add_argument("datafile")
    args = parser.parse_args()

    return args


def load_sim_live_dataset(dataset_file):
    """
    Read in the csv stock data file as a pandas dataframe
    param <str> dataset_file: the path to the live stock data file
    return <class 'pandas.core.frame.DataFrame'> data: dataframe containing the live stock data
    """
    data = pd.read_csv(dataset_file)
    return data


def get_simulated_live_data(dataset_series_row):
    """
    Turns a row of live stock price data into a dictionary
    param <class 'pandas.core.series.Series'> dataset_series_row: series containing live stock data
    return <dict[<str>:float]>> stock_prices: the live stock data prices
    """
    stock_prices = dataset_series_row.drop(labels=['Datetime']).to_dict()
    return stock_prices


def get_live_data():
    """
    Gets the current real-time prices for a predefined set of stocks
    return <dict[<str>:float]>> stock_prices: the real-time stock data prices
    """
    stock_prices = {}
    try:
        for ticker in STOCKS_WATCHLIST:
            stock_prices[ticker] = yahoo_fin.stock_info.get_live_price(ticker)
        return stock_prices
    except Exception as e:
        #some issue retrieving data with yahoo_fin.stock_info.get_live_price(ticker)
        return {}
    return {}


def buy(buy_list, stock_prices):
    """
    Simulate purchasing stocks
    param <list<tuple>> buy_list: the list containing stock, quantity pairs
    param <dict[<str>:float]>> stock_prices: the stock data prices
    """
    #eventually replace with robinhood buy
    global CASH

    for ticker, quantity in buy_list:
        price = round(stock_prices[ticker], 2)
        if ticker in STOCK_PORTFOLIO:
            STOCK_PORTFOLIO[ticker] += quantity
        else:
            STOCK_PORTFOLIO[ticker] = quantity
        CASH -= quantity * price
        CASH = round(CASH, 2)
        print("Bought", quantity, "shares of", ticker, "at", price, "per share for a total of", quantity * price) #add time element?


def sell(sell_list, stock_prices):
    """
    Simulate selling stocks
    param <list<tuple>> sell_list: the list containing stock, quantity pairs
    param <dict[<str>:float]>> stock_prices: the stock data prices
    """
    #eventually replace with robinhood sell
    global CASH

    for ticker, quantity in sell_list:
        price = round(stock_prices[ticker], 2)
        STOCK_PORTFOLIO[ticker] -= quantity
        if STOCK_PORTFOLIO[ticker] == 0:
            del STOCK_PORTFOLIO[ticker]
        CASH += quantity * price
        CASH = round(CASH, 2)
        print("Sold", quantity, "shares of", ticker, "at", price, "per share for a total of", quantity * price) #add time element?


def pretty_print_stock_prices(stock_prices):
    """
    Neatly print out stock prices to console
    param <dict[<str>:float]>> stock_prices: the stock data prices
    """
    print("\nSTOCK PRICES")
    print("---------------")
    for ticker in stock_prices:
        print(ticker + "\t" + str(round(stock_prices[ticker], 2)))
    print("---------------\n")


def pretty_print_porfolio_standing(stock_prices):
    """
    Neatly printe out quantity of each stock own, its unit values, cash available to spend, and total worth of portfolio
    param <dict[<str>:float]>> stock_prices: the stock data prices
    """
    print("=======================")
    print("CURRENT POSITION")
    print("=======================")
    print("Stock\tShares\tValue")
    total_worth = CASH
    for ticker in STOCK_PORTFOLIO:
        shares = STOCK_PORTFOLIO[ticker]
        curr_val = round(stock_prices[ticker], 2)
        total_worth += shares * curr_val
        total_worth = round(total_worth, 2)
        print(ticker + "\t" + str(shares) + "\t" + str(curr_val))
    print("Cash:", CASH)
    print("Total Worth:", total_worth)
    print("=======================")


def during_trading_hours():
    """
    Returns true if current time is between 9:30 AM and 4:00 PM US eastern time, false otherwise
    return <boolean>: True if normal trading hours, False otherwise
    """
    time_now = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    nyse_open = time_now.replace(hour=9, minute=30, second=0, microsecond=0)
    nyse_close = time_now.replace(hour=16, minute=0, second=0, microsecond=0)
    return time_now >= nyse_open and time_now <= nyse_close


if __name__ == "__main__":
    main()