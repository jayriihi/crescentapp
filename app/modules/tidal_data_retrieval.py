import requests
import pandas as pd
from datetime import datetime, timedelta
import json

def fetch_hilo_tide_predictions(station_id, start_date, end_date):
    """Fetch high and low tide predictions."""
    params = {
        "station": station_id,
        "begin_date": start_date.strftime("%Y%m%d"),
        "end_date": end_date.strftime("%Y%m%d"),
        "product": "predictions",
        "datum": "MLLW",
        "interval": "hilo",
        "units": "metric",
        "time_zone": "gmt",
        "format": "json",
    }
    response = requests.get("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter", params=params)
    data = response.json()
    hilo_predictions = pd.DataFrame(data["predictions"])
    hilo_predictions['t'] = pd.to_datetime(hilo_predictions['t'])
    hilo_predictions['v'] = pd.to_numeric(hilo_predictions['v'])
    return hilo_predictions

def get_detailed_tide_predictions(station_id, start_date, end_date):
    """Fetch detailed tide predictions at 15-minute intervals."""
    params = {
        "station": station_id,
        "begin_date": start_date.strftime("%Y%m%d"),
        "end_date": end_date.strftime("%Y%m%d"),
        "product": "predictions",
        "datum": "MLLW",
        "interval": "15",  # Consider changing to "5" for finer detail if needed
        "units": "metric",
        "time_zone": "gmt",
        "format": "json",
    }
    response = requests.get("https://api.tidesandcurrents.noaa.gov/api/prod/datagetter", params=params)
    data = response.json()
    detailed_predictions = pd.DataFrame(data["predictions"])
    detailed_predictions['t'] = pd.to_datetime(detailed_predictions['t'])
    detailed_predictions['v'] = pd.to_numeric(detailed_predictions['v'])
    return detailed_predictions

def calculate_intermediate_times(hilo_predictions):
    """Calculate six evenly spaced times between each high and low tide."""
    intermediate_times = []
    for i in range(len(hilo_predictions) - 1):
        start_time = hilo_predictions.iloc[i]['t']
        end_time = hilo_predictions.iloc[i + 1]['t']
        interval_duration = (end_time - start_time) / 7
        for j in range(1, 7):
            intermediate_time = start_time + interval_duration * j
            intermediate_times.append(intermediate_time)
    #print(len(intermediate_times))
    return intermediate_times

def find_forecast_at_times(detailed_predictions, times):
    """Find the closest forecast tide height for each specified time."""
    forecast_tides = []
    for time in times:
        closest_prediction = detailed_predictions.iloc[(detailed_predictions['t'] - time).abs().argsort()[:1]]
        forecast_tides.append(closest_prediction.iloc[0]['v'])
    return forecast_tides

def get_tidal_flow_differences_json(station_id, start_date, end_date):
    # Fetch high and low tide predictions
    hilo_predictions = fetch_hilo_tide_predictions(station_id, start_date, end_date)
    
    # Calculate intermediate times between high and low tides
    intermediate_times = calculate_intermediate_times(hilo_predictions)
    
    # Fetch detailed tide predictions for the specified period
    detailed_predictions = get_detailed_tide_predictions(station_id, start_date, end_date)
    
    # Find forecast tide heights at intermediate times
    forecast_tides = find_forecast_at_times(detailed_predictions, intermediate_times)
    
    # Calculate differences between successive forecast tides for analysis
    differences = [forecast_tides[i + 1] - forecast_tides[i] for i in range(len(forecast_tides) - 1)]
    
    # Convert intermediate_times to ISO format strings within flow_data preparation
    flow_data = [{"time": intermediate_times[i].isoformat(), "difference": differences[i]} for i in range(len(differences))]
    
    # Convert the hilo_predictions to a suitable format for JSON conversion
    hilo_data = [{"time": t.isoformat(), "height": v} for t, v in zip(hilo_predictions['t'], hilo_predictions['v'])]
    
    # Separate JSON strings for flow data and hilo data
    flow_data_json = json.dumps(flow_data)
    hilo_data_json = json.dumps(hilo_data)
    
    #print(flow_data_json, hilo_data_json)
    return flow_data_json, hilo_data_json

# Example usage
station_id = 2695540  # Bermuda, St George's
start_date = datetime.now() - timedelta(days=1)
end_date = datetime.now()
flow_data_json, hilo_data_json = get_tidal_flow_differences_json(station_id, start_date, end_date)

# Depending on how you handle the response in Flask, you might send these JSON strings directly
# or encapsulate them in a response object if needed.


'''# Example usage
station_id = 2695540  # Bermuda, St George's
#start_date = datetime.now() - timedelta(days=0)
#end_date = datetime.now() + timedelta(days=0)

# Fetch high and low tide predictions
hilo_predictions = fetch_hilo_tide_predictions(station_id, start_date, end_date)

# Calculate intermediate times between high and low tides
intermediate_times = calculate_intermediate_times(hilo_predictions)

# Fetch detailed tide predictions
detailed_predictions = get_detailed_tide_predictions(station_id, start_date, end_date)

# Find forecast tide heights at intermediate times
forecast_tides = find_forecast_at_times(detailed_predictions, intermediate_times)
print("Forecast Tides at Intermediate Times:", forecast_tides)

# Calculate differences between successive forecast tides for analysis
differences = [forecast_tides[i+1] - forecast_tides[i] for i in range(len(forecast_tides)-1)]
print("Tidal Flow Differences:", differences)'''




'''import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_detailed_tide_predictions(station_id, start_date_str, end_date_str, interval='15'):
    """
    Fetch detailed tide predictions from NOAA for a given station, start and end dates, and interval.
    """
    base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "station": station_id,
        "begin_date": start_date_str,
        "end_date": end_date_str,
        "product": "predictions",
        "datum": "MLLW",
        "interval": interval,  # Fetch predictions at the specified interval (e.g., every 15 minutes)
        "units": "metric",
        "time_zone": "gmt",
        "format": "json",
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return pd.DataFrame(data["predictions"])

def calculate_tidal_flow_intervals(tidal_data):
    """
    Calculate tidal flow intervals from detailed tidal data.
    """
    tidal_data["Tidal_Height"] = pd.to_numeric(tidal_data["v"], errors='coerce')
    tidal_data["Date"] = pd.to_datetime(tidal_data["t"])

    interval_flows = {'Start_Time': [], 'Height_Change': []}
    for i in range(len(tidal_data) - 1):
        interval_flows['Start_Time'].append(tidal_data.iloc[i]['Date'])
        height_change = tidal_data.iloc[i + 1]['Tidal_Height'] - tidal_data.iloc[i]['Tidal_Height']
        interval_flows['Height_Change'].append(height_change)
    
    return pd.DataFrame(interval_flows)

def get_noaa_tidal_data(station_id, start_date, end_date):
    """
    Retrieve and process detailed tide predictions for a given station and date range.
    """
    # Convert dates to strings
    start_date_str = start_date.strftime("%Y%m%d")
    end_date_str = end_date.strftime("%Y%m%d")

    # Fetch detailed tide predictions
    detailed_tidal_data = fetch_detailed_tide_predictions(station_id, start_date_str, end_date_str, interval='15')

    # Calculate tidal flow intervals directly from detailed predictions
    flow_intervals_data = calculate_tidal_flow_intervals(detailed_tidal_data)
    print("Tidal Flow Intervals Data (before JSON conversion):")
    print(flow_intervals_data.head(10).to_string())  # Adjust the number of rows as needed

    flow_intervals_data_json = flow_intervals_data.to_json(orient="records", date_format="iso")
    print("\nFlow Intervals Data JSON:")
    print(flow_intervals_data_json)
    return flow_intervals_data_json

# Example usage
station_id = "2695540"  # Use an appropriate station ID
start_date = datetime.now() - timedelta(days=1)
end_date = datetime.now() + timedelta(days=1)
flow_intervals_data_json = get_noaa_tidal_data(station_id, start_date, end_date)
print(flow_intervals_data_json)'''


'''import requests
import pandas as pd
from datetime import datetime, timedelta

def calculate_tidal_flow_intervals(tidal_data):
    interval_flows = {'Start_Time': [], 'End_Time': [], 'Height_Change': []}
    for i in range(len(tidal_data) - 1):
        start_time = tidal_data.iloc[i]['Date']
        end_time = tidal_data.iloc[i + 1]['Date']
        start_height = tidal_data.iloc[i]['Tidal_Height']
        end_height = tidal_data.iloc[i + 1]['Tidal_Height']
        
        # Ensure alternating types to calculate flow between high and low (or low and high)
        if tidal_data.iloc[i]['type'] != tidal_data.iloc[i + 1]['type']:
            total_height_change = end_height - start_height
            interval_height_change = total_height_change / 6
            total_time = end_time - start_time
            interval_time = total_time / 6
            
            for j in range(1, 7):
                interval_start_time = start_time + interval_time * (j - 1)
                interval_end_time = start_time + interval_time * j
                interval_flows['Start_Time'].append(interval_start_time)
                interval_flows['End_Time'].append(interval_end_time)
                interval_flows['Height_Change'].append(interval_height_change)
    
    return pd.DataFrame(interval_flows)

def get_noaa_tidal_data(start_date, end_date):
    base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    station_id = "2695540"
    product = "predictions"
    datum = "MLLW"
    units = "english"
    start_date_str = start_date.strftime("%Y%m%d")
    end_date_str = end_date.strftime("%Y%m%d")

    params = {
        "begin_date": start_date_str,
        "end_date": end_date_str,
        "station": station_id,
        "product": product,
        "datum": datum,
        "interval": "hilo",
        "units": units,
        "time_zone": "lst_ldt",
        "format": "json"
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    tidal_data = pd.DataFrame(data["predictions"])
    tidal_data["t"] = pd.to_datetime(tidal_data["t"])
    tidal_data.rename(columns={"t": "Date", "v": "Tidal_Height", "type": "type"}, inplace=True)
    tidal_data["Tidal_Height"] = pd.to_numeric(tidal_data["Tidal_Height"], errors="coerce")

    # Calculate tidal flow intervals directly
    flow_intervals_data = calculate_tidal_flow_intervals(tidal_data)
    print("Tidal Flow Intervals Data (before JSON conversion):")
    print(flow_intervals_data)

    flow_intervals_data_json = flow_intervals_data.to_json(orient="records", date_format="iso")
    return flow_intervals_data_json

# Example usage
start_date = datetime.now() - timedelta(days=1)
end_date = datetime.now() + timedelta(days=1)
flow_intervals_data_json = get_noaa_tidal_data(start_date, end_date)
print(flow_intervals_data_json)'''



# Example usage
'''start_date = datetime(2024, 3, 1)
end_date = datetime(2024, 3, 2)
tidal_json = get_noaa_tidal_data(start_date, end_date)'''


# For demonstration, printing the JSON
#print(tidal_json)






'''def get_noaa_tidal_data(start_date, end_date):
    base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    station_id = "9751639"  # NOAA station ID for NOAA EssO Pier, Bermuda
    product = "predictions"  # Predictions for tides
    datum = "MLLW"           # Mean Lower Low Water (MLLW) datum
    units = "english"        # English units for tidal height

    # Format dates
    start_date_str = start_date.strftime("%Y%m%d")
    end_date_str = end_date.strftime("%Y%m%d")

    # Request tidal data from NOAA API
    params = {
        "begin_date": start_date_str,
        "end_date": end_date_str,
        "station": station_id,
        "product": product,
        "datum": datum,
        "units": units,
        "time_zone": "gmt",
        "format": "json"
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    # Extract and format data into a DataFrame
    tidal_data = pd.DataFrame(data["predictions"])
    tidal_data["Date"] = pd.to_datetime(tidal_data["t"])
    tidal_data.set_index("Date", inplace=True)
    tidal_data.drop(columns=["t"], inplace=True)
    tidal_data["Tidal_Height"] = tidal_data["v"].astype(float)

    # Convert tidal heights from meters to feet
    #tidal_data["Tidal_Height"] *= 3.28084  # Apply the conversion here

    # Calculate tidal differences
    tidal_data["Tidal_Difference"] = tidal_data["Tidal_Height"].diff()

    return tidal_data'''

