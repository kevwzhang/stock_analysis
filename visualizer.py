import argparse
import pandas as pd
import plotly.graph_objs

FILEPATH = "datasets/"

def main():
    """"
    Graphs historical summary data of stock OHLC values for a day
    """
    args = init_parser()
    data = import_data(args.filename)
    graph_hist(data, args.filename)


def init_parser():
    """
    Parses user input to determine which dataset to graph
    Example command use: python3 visualizer.py 2021-02-17_SNAP_hist.csv
    arg filename: name of the csv file containing the summary data
    return <class 'argparse.Namespace'> args: the argument values the user provides
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    return args


def import_data(file):
    """
    Reads stock summary csv data into a pandas dataframe
    param <string> file: name of the file containing summary stock data
    return <class 'pandas.core.frame.DataFrame'> data: dataframe containing summary stock data
    """
    data = pd.read_csv(FILEPATH + file).set_index('Datetime')
    print(type(data))
    return data


def graph_hist(data, graph_title):
    """
    Reads stock summary csv data into a pandas dataframe
    param <class 'pandas.core.frame.DataFrame'> data: dataframe containing summary stock data
    param <string> graph_title: title name for the graph
    """
    fig = plotly.graph_objs.Figure()

    fig.add_trace(
        plotly.graph_objs.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='market data'
        )
    )

    #graoh Title
    fig.update_layout(title=graph_title, yaxis_title='Stock Price (USD per Shares)')

    #x axes
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label='15min', step='minute', stepmode='backward'),
                dict(count=45, label='45min', step='minute', stepmode='backward'),
                dict(count=1, label='HTD', step='hour', stepmode='todate'),
                dict(count=3, label='3h', step='hour', stepmode='backward'),
                dict(step='all')
            ])
        )
    )

    fig.show()


if __name__ == "__main__":
    main()
