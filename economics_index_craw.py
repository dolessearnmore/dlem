from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
# Load environment variables from .env file
load_dotenv()

def get_economic_indicators():
    api_key = os.getenv('ST_LOUIS_FRED_KEY')
    # URL to fetch important economic indicators (e.g., GDP, inflation, etc.)
    base_url = "https://api.stlouisfed.org/fred/"

    obs_endpoint = 'series/observations'
    series_id = "UNRATE"
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
    
    if response.status_code == 200:
        res_data = response.json()
        #print(json.dumps(res_data, indent=4))
        # Pretty-print the JSON data with indentation
        #pretty_data = json.dumps(data, indent=4)
        #return pretty_data
        obs_data = pd.DataFrame(res_data['observations'])
        obs_data['date'] = pd.DataFrame(obs_data['date'])
        obs_data.set_index('date', inplace=True)
        obs_data['value'] = obs_data['value'].astype(float)
        return obs_data
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

indicators = get_economic_indicators()
print(indicators)
# Example of printing key economic events