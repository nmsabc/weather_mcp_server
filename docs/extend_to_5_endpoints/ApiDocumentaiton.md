# One Call API 3.0


## how to test
### server side
```bash
```bash
export OPENWEATHER_API_KEY="..."
python main.py server
#or
python ./mcp_server.py
```
### client side

```bash
python main.py forecast --lat 45.75 --lon 21.22
```

## call to the API
https://openweathermap.org/api/one-call-3#current

One Call API 3.0 contains 5 endpoints and provides access to various data:

Current weather and forecasts:
minute forecast for 1 hour
hourly forecast for 48 hours
daily forecast for 8 days
and government weather alerts
Weather data for any timestamp for 46+ years historical archive and 4 days ahead forecast
Daily aggregation of weather data for 46+ years archive and 1.5 years ahead forecast
Weather overview with a human-readable weather summary for today and tomorrow's forecast, utilizing OpenWeather AI technologies
AI Weather Assistant for retrieving weather data and weather-related advice in a human-readable and friendly format.

## pricing

Pay as you call
First 1000 API calls per day are FREE
Each additional call costs 0.0014 EUR

## how to call API

https://api.openweathermap.org/data/3.0/onecall?lat=33.44&lon=-94.04&appid={API key}

## filled with end points data

https://api.openweathermap.org/data/3.0/onecall?lat=45.7538355&lon=21.2257474&appid={xxxyyyzzz}
 
the old key was exposed - I just removed it - 31 Dec 2025 - 

## Example of API response

```json             
{
   "lat":33.44,
   "lon":-94.04,
   "timezone":"America/Chicago",
   "timezone_offset":-18000,
   "current":{
      "dt":1684929490,
      "sunrise":1684926645,
      "sunset":1684977332,
      "temp":292.55,
      "feels_like":292.87,
      "pressure":1014,
      "humidity":89,
      "dew_point":290.69,
      "uvi":0.16,
      "clouds":53,
      "visibility":10000,
      "wind_speed":3.13,
      "wind_deg":93,
      "wind_gust":6.71,
      "weather":[
         {
            "id":803,
            "main":"Clouds",
            "description":"broken clouds",
            "icon":"04d"
         }
      ]
   },
   "minutely":[
      {
         "dt":1684929540,
         "precipitation":0
      },
      ...
   ],
   "hourly":[
      {
         "dt":1684926000,
         "temp":292.01,
         "feels_like":292.33,
         "pressure":1014,
         "humidity":91,
         "dew_point":290.51,
         "uvi":0,
         "clouds":54,
         "visibility":10000,
         "wind_speed":2.58,
         "wind_deg":86,
         "wind_gust":5.88,
         "weather":[
            {
               "id":803,
               "main":"Clouds",
               "description":"broken clouds",
               "icon":"04n"
            }
         ],
         "pop":0.15
      },
      ...
   ],
   "daily":[
      {
         "dt":1684951200,
         "sunrise":1684926645,
         "sunset":1684977332,
         "moonrise":1684941060,
         "moonset":1684905480,
         "moon_phase":0.16,
         "summary":"Expect a day of partly cloudy with rain",
         "temp":{
            "day":299.03,
            "min":290.69,
            "max":300.35,
            "night":291.45,
            "eve":297.51,
            "morn":292.55
         },
         "feels_like":{
            "day":299.21,
            "night":291.37,
            "eve":297.86,
            "morn":292.87
         },
         "pressure":1016,
         "humidity":59,
         "dew_point":290.48,
         "wind_speed":3.98,
         "wind_deg":76,
         "wind_gust":8.92,
         "weather":[
            {
               "id":500,
               "main":"Rain",
               "description":"light rain",
               "icon":"10d"
            }
         ],
         "clouds":92,
         "pop":0.47,
         "rain":0.15,
         "uvi":9.23
      },
      ...
   ],
    "alerts": [
    {
      "sender_name": "NWS Philadelphia - Mount Holly (New Jersey, Delaware, Southeastern Pennsylvania)",
      "event": "Small Craft Advisory",
      "start": 1684952747,
      "end": 1684988747,
      "description": "...SMALL CRAFT ADVISORY REMAINS IN EFFECT FROM 5 PM THIS\nAFTERNOON TO 3 AM EST FRIDAY...\n* WHAT...North winds 15 to 20 kt with gusts up to 25 kt and seas\n3 to 5 ft expected.\n* WHERE...Coastal waters from Little Egg Inlet to Great Egg\nInlet NJ out 20 nm, Coastal waters from Great Egg Inlet to\nCape May NJ out 20 nm and Coastal waters from Manasquan Inlet\nto Little Egg Inlet NJ out 20 nm.\n* WHEN...From 5 PM this afternoon to 3 AM EST Friday.\n* IMPACTS...Conditions will be hazardous to small craft.",
      "tags": [

      ]
    },
    ...
  ]
}
```

## Fields in API response
If you do not see some of the parameters in your API response it means that these weather phenomena are just not happened for the time of measurement for the city or location chosen. Only really measured or calculated data is displayed in API response.
lat Latitude of the location, decimal (−90; 90)
lon Longitude of the location, decimal (-180; 180)
timezone Timezone name for the requested location
timezone_offset Shift in seconds from UTC
current Current weather data API response
current.dt Current time, Unix, UTC
current.sunrise Sunrise time, Unix, UTC. For polar areas in midnight sun and polar night periods this parameter is not returned in the response
current.sunset Sunset time, Unix, UTC. For polar areas in midnight sun and polar night periods this parameter is not returned in the response
current.temp Temperature. Units - default: kelvin, metric: Celsius, imperial: Fahrenheit. How to change units used
current.feels_like Temperature. This temperature parameter accounts for the human perception of weather. Units – default: kelvin, metric: Celsius, imperial: Fahrenheit.
current.pressure Atmospheric pressure on the sea level, hPa
current.humidity Humidity, %
current.dew_point Atmospheric temperature (varying according to pressure and humidity) below which water droplets begin to condense and dew can form. Units – default: kelvin, metric: Celsius, imperial: Fahrenheit
current.clouds Cloudiness, %
current.uvi Current UV index.
current.visibility Average visibility, metres. The maximum value of the visibility is 10 km
current.wind_speed Wind speed. Wind speed. Units – default: metre/sec, metric: metre/sec, imperial: miles/hour. How to change units used
current.wind_gust (where available) Wind gust. Units – default: metre/sec, metric: metre/sec, imperial: miles/hour. How to change units used
current.wind_deg Wind direction, degrees (meteorological)
current.rain
current.rain.1h (where available) Precipitation, mm/h. Please note that only mm/h as units of measurement are available for this parameter
current.snow
current.snow.1h (where available) Precipitation, mm/h. Please note that only mm/h as units of measurement are available for this parameter
current.weather
current.weather.id Weather condition id
current.weather.main Group of weather parameters (Rain, Snow etc.)
current.weather.description Weather condition within the group (full list of weather conditions). Get the output in your language
current.weather.icon Weather icon id. How to get icons
minutely Minute forecast weather data API response
minutely.dt Time of the forecasted data, unix, UTC
minutely.precipitation Precipitation, mm/h. Please note that only mm/h as units of measurement are available for this parameter
hourly Hourly forecast weather data API response
hourly.dt Time of the forecasted data, Unix, UTC
hourly.temp Temperature. Units – default: kelvin, metric: Celsius, imperial: Fahrenheit. How to change units used
hourly.feels_like Temperature. This accounts for the human perception of weather. Units – default: kelvin, metric: Celsius, imperial: Fahrenheit.
hourly.pressure Atmospheric pressure on the sea level, hPa
hourly.humidity Humidity, %
hourly.dew_point Atmospheric temperature (varying according to pressure and humidity) below which water droplets begin to condense and dew can form. Units – default: kelvin, metric: Celsius, imperial: Fahrenheit.
hourly.uvi UV index
hourly.clouds Cloudiness, %
hourly.visibility Average visibility, metres. The maximum value of the visibility is 10 km
hourly.wind_speed Wind speed. Units – default: metre/sec, metric: metre/sec, imperial: miles/hour.How to change units used
hourly.wind_gust (where available) Wind gust. Units – default: metre/sec, metric: metre/sec, imperial: miles/hour. How to change units used
hourly.wind_deg Wind direction, degrees (meteorological)
hourly.pop Probability of precipitation. The values of the parameter vary between 0 and 1, where 0 is equal to 0%, 1 is equal to 100%
hourly.rain
hourly.rain.1h (where available) Precipitation, mm/h. Please note that only mm/h as units of measurement are available for this parameter
hourly.snow
hourly.snow.1h (where available) Precipitation, mm/h. Please note that only mm/h as units of measurement are available for this parameter
hourly.weather
hourly.weather.id Weather condition id
hourly.weather.main Group of weather parameters (Rain, Snow etc.)
hourly.weather.description Weather condition within the group (full list of weather conditions). Get the output in your language
hourly.weather.icon Weather icon id. How to get icons
daily Daily forecast weather data API response
daily.dt Time of the forecasted data, Unix, UTC
daily.sunrise Sunrise time, Unix, UTC. For polar areas in midnight sun and polar night periods this parameter is not returned in the response
daily.sunset Sunset time, Unix, UTC. For polar areas in midnight sun and polar night periods this parameter is not returned in the response
daily.moonrise The time of when the moon rises for this day, Unix, UTC
daily.moonset The time of when the moon sets for this day, Unix, UTC
daily.moon_phase Moon phase. 0 and 1 are 'new moon', 0.25 is 'first quarter moon', 0.5 is 'full moon' and 0.75 is 'last quarter moon'. The periods in between are called 'waxing crescent', 'waxing gibbous', 'waning gibbous', and 'waning crescent', respectively. Moon phase calculation algorithm: if the moon phase values between the start of the day and the end of the day have a round value (0, 0.25, 0.5, 0.75, 1.0), then this round value is taken, otherwise the average of moon phases for the start of the day and the end of the day is taken
summaryHuman-readable description of the weather conditions for the day
daily.temp Units – default: kelvin, metric: Celsius, imperial: Fahrenheit. How to change units used
daily.temp.morn Morning temperature.
daily.temp.day Day temperature.
daily.temp.eve Evening temperature.
daily.temp.night Night temperature.
daily.temp.min Min daily temperature.
daily.temp.max Max daily temperature.
daily.feels_like This accounts for the human perception of weather. Units – default: kelvin, metric: Celsius, imperial: Fahrenheit. How to change units used
daily.feels_like.morn Morning temperature.
daily.feels_like.day Day temperature.
daily.feels_like.eve Evening temperature.
daily.feels_like.night Night temperature.
daily.pressure Atmospheric pressure on the sea level, hPa
daily.humidity Humidity, %
daily.dew_point Atmospheric temperature (varying according to pressure and humidity) below which water droplets begin to condense and dew can form. Units – default: kelvin, metric: Celsius, imperial: Fahrenheit.
daily.wind_speed Wind speed. Units – default: metre/sec, metric: metre/sec, imperial: miles/hour. How to change units used
daily.wind_gust (where available) Wind gust. Units – default: metre/sec, metric: metre/sec, imperial: miles/hour. How to change units used
daily.wind_deg Wind direction, degrees (meteorological)
daily.clouds Cloudiness, %
daily.uvi The maximum value of UV index for the day
daily.pop Probability of precipitation. The values of the parameter vary between 0 and 1, where 0 is equal to 0%, 1 is equal to 100%
daily.rain (where available) Precipitation volume, mm. Please note that only mm as units of measurement are available for this parameter
daily.snow (where available) Snow volume, mm. Please note that only mm as units of measurement are available for this parameter
daily.weather
daily.weather.id Weather condition id
daily.weather.main Group of weather parameters (Rain, Snow etc.)
daily.weather.description Weather condition within the group (full list of weather conditions). Get the output in your language
daily.weather.icon Weather icon id. How to get icons
alerts National weather alerts data from major national weather warning systems
alerts.sender_name Name of the alert source. Please read here the full list of alert sources
alerts.event Alert event name
alerts.start Date and time of the start of the alert, Unix, UTC
alerts.end Date and time of the end of the alert, Unix, UTC
alerts.description Description of the alert
alerts.tags Type of severe weather
