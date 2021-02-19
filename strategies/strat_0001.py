STOCK_PORTFOLIO = {}
STOCKS_WATCHLIST = ['SNAP', 'UBER', 'MSFT', 'ABNB', 'AAPL']; STOCKS_WATCHLIST.sort()
MAX_STOCK_QTY = 2 #the max amount of shares willing to hold per stock
MAX_UNIT_PRICE = 100.0 #the max unit price willing to buy per share

PREV_STOCK_PRICES = {}

def main(stock_prices):
    """
    Strategy: tit for tat strategy, if a stock just increased in price, buy and if a stock just decreased, sell
    param <dict<float>> stock_prices: the stock prices
    return <dict<list<tuple>>> order: the quantity of stocks to buy and sell ex {"Buy": [(SNAP, 2)], "Sell": [(UBER, 1)]}
    """
    #if it is the first run, set previous stock prices to current prices and return an empty order
    if not PREV_STOCK_PRICES:
        for ticker in stock_prices:
            PREV_STOCK_PRICES[ticker] = stock_prices[ticker]
        return {"Buy": [], "Sell": []}

    #use tit for tat strategy
    order = execute_order(stock_prices)

    #save old prices so they can be used to compare with new prices
    for ticker in stock_prices:
        PREV_STOCK_PRICES[ticker] = stock_prices[ticker]

    return order


def execute_order(stock_prices):
    """
    Determine which stocks to sell and buy based on strategy
    param <dict<float>> stock_prices: the stock prices
    return <dict<list<tuple>>> order: the quantity of stocks to buy and sell ex {"Buy": [(SNAP, 2)], "Sell": [(UBER, 1)]}
    """
    order = {"Buy": [], "Sell": []}
    for ticker in STOCKS_WATCHLIST:
        if stock_prices[ticker] > PREV_STOCK_PRICES[ticker]: #rising
            #buy
            if ticker not in STOCK_PORTFOLIO:
                order["Buy"].append((ticker, MAX_STOCK_QTY))
                STOCK_PORTFOLIO[ticker] = MAX_STOCK_QTY
                continue
        if stock_prices[ticker] < PREV_STOCK_PRICES[ticker]: #going down
            #sell
            if ticker in STOCK_PORTFOLIO:
                order["Sell"].append((ticker, MAX_STOCK_QTY))
                del STOCK_PORTFOLIO[ticker]

    return order