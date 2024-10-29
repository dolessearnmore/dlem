import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

def simple_get_data(rates, symbol):
    if rates is not None and rates.size > 0:
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        plt.figure(figsize=(10, 4))
        plt.plot(df['time'], df['close'], label='Close Price', color='blue')
        plt.title(f'Close Price of {symbol} Over Time')
        plt.xlabel('Time')
        plt.ylabel('Close Price')
        plt.legend()
        plt.show()
    else:
        print(f"No data for {symbol} in the specified time range.")

def get_current_data(symbol, start_time, end_time, timeframe):
    """
    Fetches the latest `count` number of historical data for a given symbol and timeframe.

    Args:
        symbol (str): The MT5 symbol (e.g., "XAUUSDm").
        timeframe (int): The MT5 timeframe constant (e.g., mt5.TIMEFRAME_M1 for M1).
        count (int): The number of data points to retrieve.

    Returns:
        pandas.DataFrame: A DataFrame containing the historical data,
                          None otherwise.
    """
    #rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start_time, end_time)
    rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
    print(rates)
    if rates is not None:
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df
    else:
        print(f"No data for {symbol}")
        return None
    
def save_to_csv(df, filename):
    """
    Saves the DataFrame to a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame to save.
        filename (str): The filename for the CSV file.
    """

    df.to_csv(filename)
def main():
    """
    Main function that loads environment variables, initializes MT5, retrieves data,
    and saves it to a CSV file.
    """

    # Load environment variables from .env file (optional)
    load_dotenv()
    ACCOUNT = os.getenv('ACCOUNT')
    SERVER = os.getenv('SERVER')
    PASSWORD = os.getenv("PASSWORD")

    if not mt5.initialize(login=int(ACCOUNT), server=SERVER,password=PASSWORD):
        print("initialize() failed, error code =",mt5.last_error())
        quit()
    symbol = "XAUUSDm"
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=1440)
    time_frame = mt5.TIMEFRAME_M1
    time_frame2 = mt5.TIMEFRAME_H1
    print(time_frame2)
    #rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start_time, end_time)
    df = get_current_data(symbol, start_time, end_time, time_frame)
    filename = f"{symbol}_m1_data.csv"
    save_to_csv(df, filename)
    print(f"Data saved to {filename}")
    print(mt5.terminal_info())

if __name__ == "__main__":
    main()