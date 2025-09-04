from flask import Flask, render_template, request
import requests
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA 
# from pmdarima import auto_arima
import warnings
import matplotlib
from datetime import datetime, timedelta
import json   

app = Flask(__name__)

search_done = False
matplotlib.use('Agg')

@app.route('/', methods=['GET', 'POST'])
def home():
    search_done = False
    API_KEY = "71fe11b297f5478abe0315d898d97baa"

    if request.method == "POST":
        city = request.form['city']
        current_data = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        )
        data_for_current_temp = current_data.json()

        # Agar city galat ho ya API se error aaye
        if data_for_current_temp.get("cod") != 200:
            return render_template('404_error.html')

        # Sahi data
        city_name = data_for_current_temp['name']
        current_temp = round(data_for_current_temp['main']['temp'])
        feels_like = round(data_for_current_temp['main']['feels_like'])
        temp_min = round(data_for_current_temp['main']['temp_min'])
        temp_max = round(data_for_current_temp['main']['temp_max'])
        humidity = round(data_for_current_temp['main']['humidity'])
        country = data_for_current_temp['sys']['country']
        description = data_for_current_temp['weather'][0]['description']
        search_done = True

        return render_template(
            'index.html',
            city=city_name,
            current_temp=current_temp,
            temp_max=temp_max,
            temp_min=temp_min,
            description=description,
            feels_like=feels_like,
            country=country,
            status=search_done,
            humidity=humidity
        )

    return render_template("index.html", status=search_done)


API_KEY = "71fe11b297f5478abe0315d898d97baa"


@app.route('/predict-weather', methods=['GET', 'POST'])
def prediction():
    predict_status = False
    if request.method == "POST":
        city = request.form['city']
        try:
            # Current Weather API
            current_data = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            )
            data_for_current_temp = current_data.json()

            # Agar city galat hai to error page dikhao
            if data_for_current_temp.get("cod") != 200:
                return render_template('404_error.html')

            # Lat, Lon nikaalo
            LAT = data_for_current_temp['coord']['lat']
            LON = data_for_current_temp['coord']['lon']

           
            parameters = {
                "lat": LAT,
                "lon": LON,
                "appid": API_KEY,
                "units": "metric",
                "exclude": "minutely,hourly,alerts"
            }

            response = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=parameters)


            response.raise_for_status()
            data = response.json()

            # DATA SLICING
            temperature = []
            humidity = []
            hours = []

            for i in range(40):  # 5 din ka forecast (3-3 hours interval)
               hourly_data = data['list'][i]
               hours.append(i*3)  # kyunki 3-3 ghante ka data hai
               temperature.append(hourly_data['main']['temp'])
               humidity.append(hourly_data['main']['humidity'])


            # Reverse karna ho
            hours = hours[::-1]
            temperature = temperature[::-1]
            humidity = humidity[::-1]

            # DATA MODELLING
            dict_data = {'hours': hours, 'temp': temperature, 'hum': humidity}
            df = pd.DataFrame(dict_data)
            df.to_csv('static/csv/weather_data.csv', index=False)

            # MACHINE LEARNING MODEL
            data_csv = pd.read_csv("static/csv/weather_data.csv")
            data_csv = data_csv.dropna()

            weather_data = data_csv['temp']
            hum_data = data_csv['hum']

            warnings.filterwarnings("ignore")

            model_temp = ARIMA(weather_data, order=(1, 1, 1))
            model_temp_fit = model_temp.fit()

            model_hum = ARIMA(hum_data, order=(1, 1, 1))
            model_hum_fit = model_hum.fit()

            # Future hours (5 predictions)
            s_index_future_hours = [
                (datetime.now() + timedelta(hours=i)).strftime("%H:%M") for i in range(5)
            ]

            # Temperature predictions
            weather_pred = model_temp_fit.predict(start=48, end=52, typ='levels')
            weather_pred.index = s_index_future_hours
            list_file = weather_pred.tolist()

            temperature_1, temperature_2, temperature_3, temperature_4, temperature_5 = \
                [round(val, 1) for val in list_file[:5]]

            # Humidity predictions
            hum_pred = model_hum_fit.predict(start=48, end=52, typ='levels')
            hum_pred.index = s_index_future_hours
            list_file2 = hum_pred.tolist()

            humidity_1, humidity_2, humidity_3, humidity_4, humidity_5 = \
                [round(val, 1) for val in list_file2[:5]]

            # Current Weather Data
            current_data = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            )
            data_for_current_temp = current_data.json()

            city_name = data_for_current_temp['name']
            current_temp = round(data_for_current_temp['main']['temp'])
            feels_like = round(data_for_current_temp['main']['feels_like'], 1)
            temp_min = round(data_for_current_temp['main']['temp_min'], 1)
            temp_max = round(data_for_current_temp['main']['temp_max'], 1)
            humidity_now = round(data_for_current_temp['main']['humidity'], 1)
            country = data_for_current_temp['sys']['country']
            description = data_for_current_temp['weather'][0]['description']

            predict_status, search_done = True, True

            # Graph Data
            graph_temp = [
                (s_index_future_hours[0], temperature_1),
                (s_index_future_hours[1], temperature_2),
                (s_index_future_hours[2], temperature_3),
                (s_index_future_hours[3], temperature_4),
                (s_index_future_hours[4], temperature_5),
            ]
            tlabels, tvalues = zip(*graph_temp)

            graph_hum = [
                (s_index_future_hours[0], humidity_1),
                (s_index_future_hours[1], humidity_2),
                (s_index_future_hours[2], humidity_3),
                (s_index_future_hours[3], humidity_4),
                (s_index_future_hours[4], humidity_5),
            ]
            hlabels, hvalues = zip(*graph_hum)
            
            return render_template(
                "index.html",
                predicted_temp=weather_pred,
                predicted_humidity=hum_pred,
                predict_status=predict_status,
                status=search_done,
                temperature_1=temperature_1,
                temperature_2=temperature_2,
                temperature_3=temperature_3,
                temperature_4=temperature_4,
                temperature_5=temperature_5,
                humidity_1=humidity_1,
                humidity_2=humidity_2,
                humidity_3=humidity_3,
                humidity_4=humidity_4,
                humidity_5=humidity_5,
                city=city_name,
                current_temp=current_temp,
                temp_max=temp_max,
                temp_min=temp_min,
                description=description,
                feels_like=feels_like,
                country=country,
                humidity=humidity_now,
                tlabels=tlabels,
                tvalues=tvalues,
                hlabels=hlabels,
                hvalues=hvalues
            )

        except Exception as e:
            print("Error:", e)
            return render_template("404_error.html")

    return render_template("predict.html", status=predict_status)

if __name__ == "__main__":
    app.run(debug=True)
