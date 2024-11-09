from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from gg_services import process_and_upload_data, load_data_to_bigquery
# Load environment variables from .env file
load_dotenv()

def get_economic_indicators(series_id, data_type):
    """
    Fetches economic data (UNRATE, CPI, etc.) from the St. Louis Fed API and saves it to a CSV file.
    
    :param series_id: The series ID for the economic data (e.g., 'UNRATE', 'CPIAUCSL').
    :param data_type: A string describing the type of data being fetched (e.g., 'unemployment', 'cpi').
    :return: A DataFrame with the fetched data.
    """
    api_key = os.getenv('ST_LOUIS_FRED_KEY')
    # URL to fetch important economic indicators (e.g., GDP, inflation, etc.)
    base_url = "https://api.stlouisfed.org/fred/"

    obs_endpoint = 'series/observations'
    end_date = datetime.now()
    start_date =  end_date - timedelta(days=365 * 24)
    #ts_frequency = "q"
    ts_units="pc1"
    obs_params = {
        'series_id' : series_id,
        'api_key': api_key,
        'file_type': 'json',
        'observation_start': start_date.strftime('%Y-%m-%d'),
        'observation_end': end_date.strftime('%Y-%m-%d'),
        #'frequency': ts_frequency,
        'units': ts_units
    }
    response = requests.get(base_url + obs_endpoint, params=obs_params)
     # Format the filename with symbol, timeframe, and dates
    #filename = f"{series_id}_{timeframe_str}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
    if response.status_code == 200:
        res_data = response.json()
        #print(json.dumps(res_data, indent=4))
        # Pretty-print the JSON data with indentation
        #pretty_data = json.dumps(data, indent=4)
        #return pretty_data
        obs_data = pd.DataFrame(res_data['observations'])
        obs_data['date'] = pd.DataFrame(obs_data['date'])
        #obs_data.set_index('date', inplace=True)
        obs_data['value'] = obs_data['value'].astype(float)
        #print(obs_data.index)
        # Format the filename and save the data to CSV
        filename = f"./Economic_Index_Craw/{data_type}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        obs_data.to_csv(filename)
        print(f"Data saved to {filename}")
        return obs_data
    else:
        print(f"Error fetching data: {response.status_code}")
        return None
def fetch_multiple_indicators():
    """
    Fetch multiple economic indicators and save each dataset as a CSV file.
    """
    indicators = {
        'UNRATE': 'unemployment',  # Unemployment rate
        'CPIAUCSL': 'cpi',         # Consumer Price Index for All Urban Consumers
        'FEDFUNDS': 'interest_rate' # Effective Federal Funds Rate
    }
    
    for series_id, data_type in indicators.items():
        print(f"Fetching data for {data_type} ({series_id})...")
        df = get_economic_indicators(series_id, data_type)
        print(df.columns)
        process_and_upload_data(df, 
                                data_type='economic', 
                                symbol=series_id, 
                                start_date=df['date'].iloc[0].replace('-', ''), 
                                end_date=df['date'].iloc[-1].replace('-', ''))
    print("Load to big query")
    # Load to Bigquery
    bucket_name = os.getenv("BUCKET_STORAGE")
    root_name = os.getenv("ECONOMIC_DATASET_ID")
    dataset_id = os.getenv("ECONOMIC_DATASET_ID")
    #print(bucket_name, root_name, dataset_id)
    load_data_to_bigquery(bucket_name=bucket_name, root_folder=root_name, dataset_id=dataset_id)
    #print("Load done")

        
def plot_line_chart(df, date_column, value_column, title='Line Chart'):
    """
    Plots a line chart with the x-axis as the date and the y-axis as values.
    
    :param df: pandas DataFrame containing the data
    :param date_column: name of the column containing dates
    :param value_column: name of the column containing values to plot on the y-axis
    :param title: Title of the chart
    """
        # Reset the index so that 'date' becomes a regular column
    df = df.reset_index()
    # Ensure the date column is in datetime format
    df[date_column] = pd.to_datetime(df[date_column])

    # Sort values by date to ensure proper plotting
    df = df.sort_values(by=date_column)

    # Plotting the line chart
    plt.figure(figsize=(10, 6))  # Set figure size
    plt.plot(df[date_column], df[value_column], label=value_column, marker='o')  # Add markers to make points visible
    
    # Add labels and title
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title(title)

    # Optional: Rotate date labels for better visibility
    plt.xticks(rotation=45)

    # Show the grid
    plt.grid(True)

    # Display the legend
    plt.legend()

    # Show the plot
    plt.tight_layout()
    plt.show()

# Example Usage:
# Assuming 'df' is your DataFrame and has columns 'Date' and 'Adj Close'
# plot_line_chart(df, 'Date', 'Adj Close', title='Gold Prices over Time')
#fetch_multiple_indicators()
# plot_line_chart(indicators, 'date', 'value', title='Unemployment rate percent change')
# Example of printing key economic events