import requests
from flask import render_template, request, session, jsonify , Flask, redirect, url_for
from app.modules import wind_data_functionsc, tide_now, sesh_tide
from app import app
from datetime import datetime, timedelta
#import pandas as pd
#import json



@app.route("/")
@app.route("/home")
def homepage():
    # Simulate fetched data (Temporary flag for testing)
    force_error = False
      # Set this to True to simulate repeated data error

    if force_error:
        print("Simulated error: Redirecting to the error page.")
        return redirect(url_for('error_2'))

    # Fetch Crescent wind data
    avg_wind_spd, wind_max, wind_min, avg_wind_dir, date_time_index_series_str, wind_spd_series = wind_data_functionsc.pearl_1hr_quik()

    # Check for Crescent outage (repeated data indicates an outage)
    is_crescent_valid = len(set(wind_spd_series)) > 1  # Crescent data is valid if there's variation
    if not is_crescent_valid:
        print("Crescent data invalid. Redirecting to error_2.")
        return redirect(url_for('error_2'))

    # Round and convert to integers for display
    avg_wind_spd = round(avg_wind_spd, 1)
    wind_max = int(round(wind_max, 0))
    wind_min = int(round(wind_min, 0))
    avg_wind_dir = int(round(avg_wind_dir, 0))

    print("Checking for repeated data in wind speed series...")
    print(f"Wind Speed Series: {wind_spd_series}")
    print(f"Unique Values in Wind Speed Series: {set(wind_spd_series)}")

    # Fetch tide data
    flow_state_beg, prev_peak_time, prev_peak_state, prev_peak_ht, next_peak_time, next_peak_state, next_peak_ht = tide_now.get_tide_data_for_now()

    # Convert tide state abbreviation to full form
    tide_state_full = "Low" if next_peak_state == "L" else "High"

    # Convert Timestamp to string and then format time to show only hours and minutes
    next_peak_time_formatted = next_peak_time.strftime('%H:%M')

    # Render the main page with live Crescent data
    return render_template(
        "graph_temp_info_tide_chart.html",
        labels=date_time_index_series_str,
        values=wind_spd_series,
        past_hour_avg_wind_spd=avg_wind_spd,
        past_hour_avg_wind_min=wind_min,
        past_hour_avg_wind_max=wind_max,
        avg_wind_dir=avg_wind_dir,
        flow_state_beg=flow_state_beg,
        prev_peak_time=prev_peak_time,
        prev_peak_state=prev_peak_state,
        prev_peak_ht=prev_peak_ht,
        next_peak_time=next_peak_time_formatted,
        next_peak_state=tide_state_full,
        next_peak_ht=next_peak_ht,
        is_modeled=False  # Indicate live data
    )




@app.route("/graph_1hr")
def graph_1hr():
    avg_wind_spd, wind_max, wind_min,avg_wind_dir, date_time_index_series_str, wind_spd_series = wind_data_functionsc.pearl_1hr_quik()

    return render_template ("graph_temp.html", labels = date_time_index_series_str, values = wind_spd_series, past_hour_avg_wind_spd = avg_wind_spd, past_hour_avg_wind_min = wind_min, past_hour_avg_wind_max = wind_max, avg_wind_dir = avg_wind_dir )

@app.route("/graph_3hr")
def graph_3hr():
    avg_wind_spd, wind_max, wind_min,avg_wind_dir, date_time_index_series_str, wind_spd_series = wind_data_functionsc.pearl_3hr_quik()

    return render_template ("graph_3hr.html", labels = date_time_index_series_str, values = wind_spd_series, past_hour_avg_wind_spd = avg_wind_spd, past_hour_avg_wind_min = wind_min, past_hour_avg_wind_max = wind_max, avg_wind_dir = avg_wind_dir )


@app.route("/graph_8hr")
def graph_8hr():
    avg_wind_spd, wind_max, wind_min,avg_wind_dir, date_time_index_series_str, wind_spd_series = wind_data_functionsc.pearl_8hr_quik()

    return render_template ("graph_8hr.html", labels = date_time_index_series_str, values = wind_spd_series, past_hour_avg_wind_spd = avg_wind_spd, past_hour_avg_wind_min = wind_min, past_hour_avg_wind_max = wind_max, avg_wind_dir = avg_wind_dir )
    #return render_template("graph_1hr.html")'''


@app.route("/windput", methods = ["POST" , "GET"])
# takes the post intputs fromer user on windput page makes them into session variables
def windput():
    if request.method == "POST":
        #getting form data and saving as session variables
        req = request.form
        #print(req)
        sessiondatetime = request.form["sessiondatetime"]
        #print(type(sessiondatetime))
        session['sessiondatetime'] = sessiondatetime

        #sessiondatetime_str = datetime.strftime(sessiondatetime)
        #session["sessiondatetime_str"] = sessiondatetime_str
        #print(session["sessiondatetime_str"])

        duration = request.form["duration"]
        session['duration'] = duration
        #print(session['duration'])
               
        return wind()
        #return render_template("windput.html",form = form)

    else:
        return_val = render_template("windput.html") 
        return return_val


@app.route("/wind")
def wind():

    #print(session['timestart'])
    #avg_wind_spd, wind_max, wind_min,sesh_start_date_str,sesh_start_time_str,h,m,avg_wind_dir = get_sesh_wind(session['sessiondatetime'],  session['duration'])

    string_start_time, string_end_time, h, m, sesh_start_date_str, sesh_start_time_str,avg_wind_spd, wind_max, wind_min,avg_wind_dir, date_time_index_series_str, wind_spd_series = wind_data_functionsc.get_sesh_wind(session['sessiondatetime'],  session['duration'])

     # Check if the data is flatlined (no variation in wind speed)
    is_crescent_down = len(set(wind_spd_series)) <= 1  # All values are the same or no data


    flow_state_beg, flow_state_end , prev_peak_time, prev_peak_state, next_peak_time, next_peak_state = sesh_tide.get_tide_data_for_session(session['sessiondatetime'],  session['duration'])
    

  

    #wind = get_sesh_wind(datetime.date(2022,5,3), datetime.time(12,00), timedelta(hours=+1, minutes=+0))
    #return render_template('wind.html', value_avg = avg_wind_spd, value_max = wind_max, value_min = wind_min,value_date = sesh_start_date_str, value_time = sesh_start_time_str, value_hours = h, value_minutes = m, value_avg_n_wind_dir = avg_wind_dir)
    return render_template('wind.html', value_avg = avg_wind_spd, value_max = wind_max, value_min = wind_min,value_date = sesh_start_date_str, value_time = sesh_start_time_str, value_hours = h, value_minutes = m, value_avg_wind_dir = avg_wind_dir, labels = date_time_index_series_str , values = wind_spd_series, flow_state_beg = flow_state_beg, flow_state_end = flow_state_end, prev_peak_time = prev_peak_time, prev_peak_state = prev_peak_state, next_peak_time = next_peak_time, next_peak_state = next_peak_state, is_crescent_down = is_crescent_down)

    #value_avg = wind[6], value_max = wind[7], value_min = wind[8],value_date = wind[4], value_time = wind[5], value_hours = wind[2], value_minutes = wind[3], value_avg_n_wind_dir = wind[9])


@app.route("/graph_temp")
def graph_temp():
    avg_wind_spd, wind_max, wind_min,avg_wind_dir, date_time_index_series_str, wind_spd_series = wind_data_functionsc.pearl_1hr_quik()

    return render_template ("graph_temp.html", labels = date_time_index_series_str, values = wind_spd_series, past_hour_avg_wind_spd = avg_wind_spd, past_hour_avg_wind_min = wind_min, past_hour_avg_wind_max = wind_max, avg_wind_dir = avg_wind_dir )
    #return render_template("graph_1hr.html")

@app.route("/crescent")
def crescent_descr():
    return render_template("crescent_descr.html")

@app.route("/error")
def error():
    return render_template("error.html")

@app.route("/error_2")
def error_2():
    # Fetch modeled data from pred_cres
    avg_wind_spd, wind_max, wind_min, avg_wind_dir, date_time_index_series_str, wind_spd_series = wind_data_functionsc.fetch_pred_cres_data()

        # Round the values for display
    # Round and convert to integers for display
    avg_wind_spd = round(avg_wind_spd, 1)
    wind_max = int(round(wind_max, 0))
    wind_min = int(round(wind_min, 0))
    avg_wind_dir = int(round(avg_wind_dir, 0))

    # Fetch tide data
    flow_state_beg, prev_peak_time, prev_peak_state, prev_peak_ht, next_peak_time, next_peak_state, next_peak_ht = tide_now.get_tide_data_for_now()

    # Convert tide state abbreviation to full form
    tide_state_full = "Low" if next_peak_state == "L" else "High"

    # Convert Timestamp to string and then format time to show only hours and minutes
    next_peak_time_formatted = next_peak_time.strftime('%H:%M')

    # Pass the data to the error_2.html template
    return render_template(
        "error_2.html",
        labels=date_time_index_series_str,
        values=wind_spd_series,
        past_hour_avg_wind_spd=avg_wind_spd,
        past_hour_avg_wind_min=wind_min,
        past_hour_avg_wind_max=wind_max,
        avg_wind_dir=avg_wind_dir,
        flow_state_beg=flow_state_beg,
        prev_peak_time=prev_peak_time,
        prev_peak_state=prev_peak_state,
        prev_peak_ht=prev_peak_ht,
        next_peak_time=next_peak_time_formatted,
        next_peak_state=tide_state_full,
        next_peak_ht=next_peak_ht,
        is_modeled=True  # Flag to indicate that modeled data is being displayed
    )



@app.route("/tide")
def tide_home():
    return render_template('chart.html')

@app.route("/data")
def data():
    # Get the current date and format it as 'yyyymmdd'
    current_date = datetime.today().strftime('%Y%m%d')

    noaa_api_url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date={current_date}&end_date={current_date}&datum=MLLW&station=2695540&time_zone=lst_ldt&units=english&interval=h&format=json"
    r = requests.get(noaa_api_url)
    data = r.json()
    
    if 'predictions' in data:
        predictions = data['predictions']
        values = [i['v'] for i in predictions]
        return jsonify({'values': values})

    return jsonify({'error': 'No data available'})

@app.route('/wind_dir')
def wind_dir():
    timestamps, wind_directions = wind_data_functionsc.wind_dir_3hours()  # Get data for the past 3 hours
    # Render the HTML template with Chart.js, passing the necessary data
    return render_template('wind_dir.html', labels=timestamps, wind_dirs=wind_directions)

@app.route('/wind_clocks')
def wind_direction():
    # Fetch the wind direction changes
    hour_change = int(wind_data_functionsc.wind_direction_change_1hour())
    three_hour_change = int(wind_data_functionsc.wind_direction_change_3hour())
    six_hour_change = int(wind_data_functionsc.wind_direction_change_6hour())

    # Render the template with these changes
    return render_template('wind_clocks.html', hour=hour_change, three_hour=three_hour_change, six_hour=six_hour_change)






@app.route('/tidal_difference')
def tidal_difference():
    # Calculate today's date for the current date
    today = datetime.now().date()
    
    # Adjusted to display data for a specific period, here 1 day before and after today for demonstration
    start_date = today - timedelta(days=1)
    end_date = today + timedelta(days=1)
    
    # Retrieve tidal flow differences data and high/low tide data from NOAA for the specified time range
    flow_data_json, hilo_data_json = get_tidal_flow_differences_json(2695540, start_date, end_date)  # Adjusted function call
    
    # No need to convert JSON to Python objects here as we're directly passing the JSON strings to the frontend

    # Pass both JSON strings to the template for rendering
    return render_template('tidal_difference.html', flow_data_json=flow_data_json, hilo_data_json=hilo_data_json)

@app.route('/dewpointplus')
def dewpoint():
    api_key = 'd6972ca477a08858bd2dbcb4bce19c55'  # Use your real API key
    lat, lon = "32.3078", "-64.7505"
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,daily,alerts&appid={api_key}&units=imperial"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        hourly_forecasts = [{
            'time': datetime.fromtimestamp(hour['dt']).strftime('%Y-%m-%d %H:%M'),
            'dew_point': hour['dew_point'],
            'temp': hour.get('temp'),  # Make sure 'temp' is the correct key
            'humidity': hour.get('humidity')  # Make sure 'humidity' is the correct key
        } for hour in data['hourly'][:72]]  # Get 72 hours of data

        # Print temperature and humidity for debugging
        '''for forecast in hourly_forecasts[:5]:  # Print the first 5 entries
            print(f"Time: {forecast['time']}, Temp: {forecast['temp']}, Humidity: {forecast['humidity']}")'''

        return render_template('dewpointplus.html', forecasts=hourly_forecasts)
    else:
        print(f"Failed to retrieve data with status code {response.status_code}")
        return f"Failed to retrieve data with status code {response.status_code}", 400


    


    

    
    

    
    