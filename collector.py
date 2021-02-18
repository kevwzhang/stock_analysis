import argparse
import datetime
import pandas as pd
import pytz
import yahoo_fin.stock_info
import yfinance

FILEPATH = "datasets/"

def main():
    """
    Collects data about stock prices and writes the data to files
    """
    args = init_parser()

    stock_list = args.stock_list.upper().split(",")
    stock_list.sort()

    if args.type == "live":
        live_data_writer(stock_list)
    elif args.type == "hist":
        get_summary_data(stock_list)
    else:
        print("bad args")


def init_parser():
    """
    Parses user input to retrieve stock data
    Example command use: python3 collector.py hist SNAP
    arg type: get the day's OHLC values for stocks or the live prices for stocks, must be 'hist' or 'live'
    arg stock_list: list of stock tickers to retrieve data for, example use 'SNAP,ABNB,UBER'
    return <class 'argparse.Namespace'> args: the argument values the user provides
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("type")
    parser.add_argument("stock_list")
    args = parser.parse_args()

    return args


def live_data_writer(tickers):
    """
    Writes live stock price data to a file - attempts to do so every second
    param <list[<str>]> tickers: list of stock tickers to get live prices
    """
    with open(FILEPATH + str(datetime.date.today()) + "_live" + ".csv", 'w') as outfile:
        file_header = "Datetime," + ",".join(tickers) + "\n"
        outfile.write(file_header)
    prev_time = datetime.datetime.now(tz=pytz.timezone('US/Eastern')).replace(microsecond=0) - datetime.timedelta(seconds=1)
    while True:
        curr_time = datetime.datetime.now(tz=pytz.timezone('US/Eastern')).replace(microsecond=0)
        if curr_time > prev_time:
            try:
                curr_prices = [str(yahoo_fin.stock_info.get_live_price(ticker)) for ticker in tickers]
            except Exception as e:
                #if there is some issue retrieving data with yahoo_fin.stock_info.get_live_price(ticker), skip the data line and continue
                print("Exception message: " + e.message)
                print("Skipping stock price retrieval for current second and continuing")
                prev_time = curr_time
                continue
            with open(FILEPATH + str(datetime.date.today()) + "_live" + ".csv", 'a') as outfile:
                outfile.write(str(curr_time) + "," + ",".join(curr_prices) + "\n")
            prev_time = curr_time


def get_summary_data(tickers):
    """
    Writes historical summary data of stock OHLC values every minute for the day to files
    param <list[<str>]> tickers: list of stock tickers to get live prices
    """
    for ticker in tickers:
        yf_data = yfinance.download(tickers=ticker, period='1d', interval='1m').reset_index()
        yf_data.to_csv(FILEPATH + str(datetime.date.today()) + "_" + ticker + "_hist" + ".csv", index=False)


def during_trading_hours():
    """
    Returns true if current time is between 9:30 AM and 4:00 PM US eastern time, false otherwise
    """
    #TODO
    pass

if __name__ == "__main__":
    main()
