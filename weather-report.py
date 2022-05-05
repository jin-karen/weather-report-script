import requests
from datetime import date,datetime
#faq https://openweathermap.org/faq#:~:text=The%20JSON%20format%20is%20used,available%20in%20the%20JSON%20format.
#response description https://openweathermap.org/weather-data
#open weather map api home https://openweathermap.org/api 
#current weather data api info https://openweathermap.org/current
#one call location with forecast data api info https://openweathermap.org/current
#geocoding api to lat long https://openweathermap.org/api/geocoding-api
current_url="https://api.openweathermap.org/data/2.5/weather"
forecast_url="https://api.openweathermap.org/data/2.5/onecall"
geocoding_zip_url="http://api.openweathermap.org/geo/1.0/zip"
geocoding_direct_url="http://api.openweathermap.org/geo/1.0/direct"
api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

def api_check():
    if api_key == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        print("Please input a valid Open Weather Api key into the api_key variable to run this script.")
        quit()

def location():
    global latitude
    global longitude
    while True:
        search = input("What city or post code would you like the weather for? ")
        city_search = search.replace(" ","")
        if search.isnumeric():
            geocoding_response = requests.get(
            geocoding_zip_url,
            headers = {"Accept":"text/plain"},
            params = {"zip": search, "appid":api_key}
            )
            geocoding_data = geocoding_response.json()
            if "cod" in geocoding_data: #and geocoding_data["cod"] == "404" (also "400"):
                print("Post code not found. Please enter something else.")
            else:
                latitude = geocoding_data["lat"]
                longitude = geocoding_data["lon"]
                break
        elif city_search.isalpha():
            geocoding_response = requests.get(
            geocoding_direct_url,
            headers = {"Accept":"text/plain"},
            params = {"q": search, "limit": 5, "appid": api_key}
            )
            geocoding_data = geocoding_response.json()
            if len(geocoding_data) == 1:
                latitude = geocoding_data[0]["lat"]
                longitude = geocoding_data[0]["lon"]
            else:
                options = []
                for x in range(len(geocoding_data)):
                    options.append(f"{x+1}. {geocoding_data[x]['name']}, {geocoding_data[x]['state']}, {geocoding_data[x]['country']}")
                print(f"There are {len(geocoding_data)} results for {search}.")
                for x in options:
                    print(x)
                city_number = int(input(f"Which one are you looking for? (Respond with corresponding number) "))
                latitude = geocoding_data[city_number-1]["lat"]
                longitude = geocoding_data[city_number-1]["lon"]
            break
        else:
            print("Please enter a valid city or post code.")

def current_temp():
    current_response = requests.get(
        current_url,
        headers = {"Accept":"application/json"},
        params = {"lat": latitude, "lon": longitude, "appid": api_key, "units": "imperial", "lang": "en"}
    )
    current_data = current_response.json()
    location = f"{current_data['name']}, {current_data['sys']['country']}"
    date = f"{datetime.utcfromtimestamp(current_data['dt']+current_data['timezone']).strftime('%b-%d-%Y %H:%M')}"
    #This finds the UTC time from the dt value and adds the timezone value for time in desired location
    #This finds local time of user: date = f"{datetime.now().strftime('%b-%d-%Y %H:%M')}"
    temperature = f"{current_data['main']['temp']} degrees Fahrenheit"
    temp_feels = f"{current_data['main']['feels_like']} degrees Fahrenheit"
    weather = f"{current_data['weather'][0]['main']} ({current_data['weather'][0]['description']})"
    report = f"\n\nCurrent Weather Report\nLocation: {location}\nDate: {date}\nTemperature: {temperature}\nFeels like: {temp_feels}\nWeather: {weather}\n"
    print(report)

def forecast_temp():
    trip_start_day = int(input("When is the first day of your trip (counting in days from today to trip start day)? "))
    trip_length = int(input("How many days of weather forecast do you need? "))
    forecast_response = requests.get(
        forecast_url,
        headers = {"Accept":"application/json"},
        params = {"lat": latitude, "lon": longitude, "appid": api_key, "exclude": "current,minutely,hourly,alerts", "units":"imperial", "lang": "en"}
    )
    forecast_data = forecast_response.json()
    if trip_start_day > 8:
        print("\nSorry, weather forecasts are only available for the next 8 days.")
    else:
        if trip_start_day + trip_length <= 9:
            num_reports = trip_start_day + trip_length - 1
        else:
            num_reports = 8
            print(f"\n\nSorry, weather forecasts are only available for the next 8 days. Come back for the remaining {trip_start_day + trip_length-9} report(s).")
        location = forecast_data['timezone']
        print(f"\n\nForecasted Weather Report\nLocation: {location}\n")
        for x in range(trip_start_day-1,num_reports):
            date = f"{datetime.utcfromtimestamp(forecast_data['daily'][x]['dt']+forecast_data['timezone_offset']).strftime('%b-%d-%Y')}"
            temperature = f"{forecast_data['daily'][x]['temp']['day']}"
            temp_feels = f"{forecast_data['daily'][x]['feels_like']['day']}"
            highest_temp = f"{forecast_data['daily'][x]['temp']['max']}"
            lowest_temp = f"{forecast_data['daily'][x]['temp']['min']}"
            weather =  f"{forecast_data['daily'][x]['weather'][0]['main']} ({forecast_data['daily'][x]['weather'][0]['description']})"
            precipitation = f"{(forecast_data['daily'][x]['pop'])*100}%"
            report = f"Date: {date}\nTemperature: {temperature}\nFeels like: {temp_feels}\nHigh: {highest_temp} Low: {lowest_temp}\nWeather: {weather}\nPrecipitation: {precipitation}\n"
            print(report)

def main():
    while True:
        api_check()
        print("Current weather gives you the weather for this moment at a desired location.")
        print("Forecasted weather gives you daily weather reports, spanning the length of your trip at a desired location.")
        choice = (input("Would you like a current weather report, forecasted weather report for a trip, or both? (c/f/b) ")).lower()
        if choice[0] == "c":
            location()
            current_temp()
            break
        elif choice[0] == "f":
            location()
            forecast_temp()
            break
        elif choice[0] == "b":
            print("Current Report:")
            location()
            current_temp()
            print("Forecasted Report:")
            location()
            forecast_temp()
            break
        else:
            print("Please enter a valid choice.")

main()
