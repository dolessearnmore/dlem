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

def init_mt5():
    ACCOUNT = os.getenv('ACCOUNT')
    SERVER = os.getenv('SERVER')
    PASSWORD = os.getenv("PASSWORD")

    if not mt5.initialize(login=int(ACCOUNT), server=SERVER,password=PASSWORD):
        print("initialize() failed, error code =",mt5.last_error())
        quit()

def get_mt5_data(symbol, time_frame, start_time, end_time):
    """
    Fetches historical data from MetaTrader 5 for the given symbol and timeframe,
    and saves it to a CSV file with the appropriate naming format.
    
    Args:
        symbol (str): The trading symbol (e.g., 'XAUUSDm').
        time_frame (int): The timeframe for the data (e.g., mt5.TIMEFRAME_D1).
        start_time (datetime): The start time for the data range.
        end_time (datetime): The end time for the data range.

    Returns:
        None
    """
    # Select the symbol
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}")
        mt5.shutdown()
        return

    # Fetch historical data
    rates = mt5.copy_rates_range(symbol, time_frame, start_time, end_time)
    
    if rates is None or len(rates) == 0:
        print("No data fetched")
        mt5.shutdown()
        return
    
    # Convert data to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')  # Convert Unix time to datetime

    # Format the timeframe string
    timeframe_str = {
        mt5.TIMEFRAME_M1: "M1",
        mt5.TIMEFRAME_M5: "M5",
        mt5.TIMEFRAME_M15: "M15",
        mt5.TIMEFRAME_M30: "M30",
        mt5.TIMEFRAME_H1: "H1",
        mt5.TIMEFRAME_H4: "H4",
        mt5.TIMEFRAME_D1: "D1"
    }.get(time_frame, str(time_frame))  # Use friendly names for common timeframes

    # Format the filename with symbol, timeframe, and dates
    filename = f"{symbol}_{timeframe_str}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.csv"

    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

    # Print terminal information
    print(mt5.terminal_info())

    # Shutdown MT5
    mt5.shutdown()
def user_interactive_data_fetch():
    """
    Interactively asks the user to choose a symbol, timeframe, and start time,
    then fetches the corresponding data from MT5 and saves it as a CSV file.

    Returns:
        None
    """
    # Initialize MT5
    if not mt5.initialize():
        print("Failed to initialize MT5")
        return

    # 1. Show available symbols and ask user to choose
    symbols = mt5.symbols_get()
    if not symbols:
        print("No symbols available in MT5.")
        mt5.shutdown()
        return

    print("\nAvailable symbols:")
    for i, symbol in enumerate(symbols[:], 1):  # Display the symbols
        print(f"{i}. {symbol.name}")

    symbol_index = int(input("\nChoose a symbol by number: ")) - 1
    symbol = symbols[symbol_index].name

    # 2. Show available timeframes and ask user to choose
    timeframes = {
        1: (mt5.TIMEFRAME_M1, "M1 (1 minute)"),
        2: (mt5.TIMEFRAME_M5, "M5 (5 minutes)"),
        3: (mt5.TIMEFRAME_M15, "M15 (15 minutes)"),
        4: (mt5.TIMEFRAME_M30, "M30 (30 minutes)"),
        5: (mt5.TIMEFRAME_H1, "H1"),
        6: (mt5.TIMEFRAME_H4, "H4"),
        7: (mt5.TIMEFRAME_D1, "D1")
    }

    print("\nAvailable timeframes:")
    for key, (_, desc) in timeframes.items():
        print(f"{key}. {desc}")

    timeframe_choice = int(input("\nChoose a timeframe by number: "))
    time_frame, timeframe_str = timeframes[timeframe_choice]

    # 3. Ask the user for the start time in years
    years_back = int(input("\nEnter the number of years back for the start time (e.g., 1 for 1 year, 2 for 2 years): "))

    # 4. Calculate the start and end times
    end_time = datetime.now()
    start_time = end_time - timedelta(days=365 * years_back)

    print(f"\nFetching data for symbol: {symbol}")
    print(f"Timeframe: {timeframe_str}")
    print(f"Start time: {start_time.strftime('%Y-%m-%d')}")
    print(f"End time: {end_time.strftime('%Y-%m-%d')}")

    # Fetch and save the data
    get_mt5_data(symbol, time_frame, start_time, end_time)