# Creating Weather Forecast App in Python using Openweathermap API and MongoDB

### Introduction:
In this app, I demonstrate how to design a Weather Forecast App that downloads weather forecast data from OpenWeatherMap using REST API and stores data in MongoDB for analysis. The weather forecast data is then shown on Google Map for each city.

OpenWeatherMap is an online service that provides current, historical and weather forecast data for analytics. To communicate with the weather data, user must subscribe to the Openweathermap website and then user can get API access key. The weather data can be downloaded simply by requesting data from server API endpoint. The data comes in JSON format.

I also used MongoDB which is a NoSQL based database for storing data. Pymongo is the library used for interfacing Mongodb with the Python code.

A detailed explanation video of this project can be viewed at https://www.youtube.com/watch?v=8rV9k2tVWWI&t=36s
### Tasks To Do:

1. Create account in https://openweathermap.org/api 
2. Get API access key by subscribing to OpenWeatherMap website
3. Make a multi-threaded program to connect to API. Locations to be monitored should be placed in configuration file
4. One thread to download 5 days/3 hour forecast
5. One thread to download weather maps
6. All data should be stored in database (mongodb) as seperate collections/table
7. One thread to open the latest weather map and display the map in window (should show last image as per last time stamp)
8. Forecast threads should print out alerts if there is rain/snow or freeezing temperatures (<2 degree Fahrenheit) in any of forecast period
9. Display forecast/previous data from database as a graph

### Prerequisites:
I am using Python 3.6 IDLE environment for coding.
Following libraries will be used in the app.
1)	Pymongo – For interfacing Python with MongoDB
2)	Threading – For creating parallel threads
3)	Json – For handling JSON data coming from APIs
4)	Httplib2 – For making http request to download API data
5)	Folium – For creating Map
6)	Seaborn – For plotting forecast data
7)	Geopy – For getting geographical coordinates of a location

To install any of the above libraries, simply open Command Prompt and install using
pip install <libraryname>

### Working:
On running the app present in the repository, the 5 day 3 hour apart forecast gets stored in MongoDB and we also get to see alerts if the weather forecast contains rainy, snowy or freezing temperatures. It also stores all the temperature maps in a folder. 

### Observations:
First, we are presented with the weather alerts in the 5 day forecast. If the weather forecast for designated cities has rain, snow or freezing temperatures (<2 Fahrenheit) then we will get weather alert. It is shown in figure below:
![weather_alerts](https://github.com/shayanalibhatti/Weather_forecast_app/blob/master/weather_alerts.jpg?raw=true)

Following image shows data for Karachi for 14th March 3am. Click to enlarge the image.
![Karachi_weather](https://github.com/shayanalibhatti/Weather_forecast_app/blob/master/weather_map.png?raw=true)

Following image shows the latest (5th day) London weather forecast for 19th March 5pm. If we click on the weather icon, in this case, the clouds, then a Popup shows the temperature.
![london_weather](https://github.com/shayanalibhatti/Weather_forecast_app/blob/master/london_latest_weather.jpg?raw=true)

Following image shows the plot of all the weathers for Utah present in database with temperature in Fahrenheit w.r.t date and time.
![utah_weather](https://github.com/shayanalibhatti/Weather_forecast_app/blob/master/utah_weather_forecast_details.jpg?raw=true)

Here is how the data in MongoDB looks like. We get temperature info, weather description, wind and timestamps.
![Mongodb](https://github.com/shayanalibhatti/Weather_forecast_app/blob/master/mongo_snap.jpg?raw=true)

### Conclusion:
In this software, I learnt to interface Mongo DB with Openweathermap API to visualize past, present and future weather forecast for analytics. I hope it will be useful to people learning about interfacing Python with Openweathermaps API and MongoDB.


