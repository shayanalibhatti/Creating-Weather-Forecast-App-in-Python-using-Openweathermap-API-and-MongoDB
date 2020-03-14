import pymongo
import configuration as config
import requests
import threading
import os
import time
from datetime import datetime
import shutil
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import httplib2
import folium
import pandas as pd
import seaborn as sns
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="Weather Forecast App")

# Settings for the OpenWeatherMap API and Folium map
open_weather_map_API_key = "8d4e8f807af8f877a9b46931b17a21cc"
open_weather_API_endpoint = "http://api.openweathermap.org/" 

# Initialized HTTPlib for HTTP requests
http_initializer = httplib2.Http()

freezing_temperature_threshold = 2 # 2 Fahrenheit

# Get city names for which we want to get forecast data from configuration file
city_names = config.locations

# How often do we want our app to refresh and download data
refresh_frequency = config.refresh_frequency


# Use this thread to download 5 days / 3 hour forecast. Also show alert if there is rain/snow or freeezing temperatures (<2 farenheit) in any of forecast period
def thread_for_5_days_3_hour_forecast():
    '''

    In this method, we download the 5 days and 3 hour separated data and store it in
    the mongodb database making timestamp as primary key, thus preventing duplicates
    
    '''
    # Initialize MongoDB client running on localhost
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    
    # Dictionary to store the alerts for rain, snow and freezing temperature
    alerts = {"rain":[],"snow":[],"freezing_temperature":[]}
    
    # We create a collection for each city to store data w.r.t. city
    for city in city_names:
        url = open_weather_API_endpoint+"/data/2.5/forecast?q="+city+"&appid="+open_weather_map_API_key
        http_initializer = httplib2.Http()
        response, content = http_initializer.request(url,'GET')
        utf_decoded_content = content.decode('utf-8')
        json_object = json.loads(utf_decoded_content)

        # Creating Mongodb database
        db = client.weather_data

        # Putting Openweathermap API data in database, with timestamp as primary key
        for element in json_object["list"]:
            try:
                datetime = element['dt']
                del element['dt']
                db['{}'.format(city)].insert_one({'_id':datetime,"data":element})
            except pymongo.errors.DuplicateKeyError:
                continue

        # Here we store the alerts based on conditions
        for a in db['{}'.format(city)].find({}):
            # Converting temperature to Fahrenheit
            temperature = (float(a["data"]["main"]["temp"]) - 273.15)*(9/5)+32 
            if temperature<freezing_temperature_threshold:
                alerts["freezing_temperature"].append("Freezing temperature "+ temperature +" in "+city+" on "+str(a["data"]["dt_txt"]).split(" ")[0]+" at "+str(a["data"]["dt_txt"]).split(" ")[1])
            elif a["data"]["weather"][0]["main"]=="Rain":
                alerts["rain"].append("Rain expected in "+city+" on "+str(a["data"]["dt_txt"]).split(" ")[0]+" at "+str(a["data"]["dt_txt"]).split(" ")[1])
            elif a["data"]["weather"][0]["main"]=="Snow":
                alerts["snow"].append("Snow expected in "+city+" on "+str(a["data"]["dt_txt"]).split(" ")[0]+" at "+str(a["data"]["dt_txt"]).split(" ")[1])

    print("*********WEATHER ALERTS********")
    if len(alerts["freezing_temperature"])>0:
        for i in alerts["freezing_temperature"]:
            print(i)
            
    if len(alerts["rain"])>0:
        for i in alerts["rain"]:
            print(i)
            
    if len(alerts["snow"])>0:
        for i in alerts["snow"]:
            print(i)

# Use this thread to download weather maps. We are simply loading the map of a location and putting icon of weather at that time on it.
def thread_for_weather_maps(locations):
    '''
        In this method, we take longitudes and latitudes of all the cities that we want for weather forecast
        We download the data from folium and put the relevant weather icon on the map.

    '''
    # Initialize MongoDB client running on localhost
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    # Access weather_data database
    db = client.weather_data

    # For each city, we call its location in Google Maps
    for city in city_names:
        for a in db['{}'.format(city)].find({}):
     
            location = locations[city]
            maps = folium.Map(location=[location.latitude, location.longitude],tiles='cartodbdark_matter', zoom_start=8,
                       attr="<a href=https://endless-sky.github.io/>Endless Sky</a>")
            weather = str(a["data"]['weather'][0]['description'])
            last_timestamp_date = str(a["data"]['dt_txt'])
            temperature = str(round(float((a["data"]["main"]["temp"] - 273.15)*(9/5)+32),2))
            # Get the icon that represents weather on that date for that city
            
            icon = a["data"]['weather'][0]['icon']   
            
            icon_url = "http://openweathermap.org/img/wn/"+icon+"@2x.png"

            # Downloading icon for the weather
            icon = folium.features.CustomIcon(icon_url,
                                              icon_size=(100, 100),
                                              icon_anchor=(22, 94),
                                              popup_anchor=(-3, -76))
                                            


            # Subtracting values just to adjust the marker on Map
            marker = folium.Marker(location=[location.latitude-0.03, location.longitude-0.12], icon=icon, popup="Temperature is "+temperature+"F", html = '<div style="font-size:12pt">%s F</div>'%temperature)
            popup = folium.Popup(temperature)

 #           folium.TileLayer('cartodbpositron').add_to(maps)
            maps.add_child(marker)
            maps.add_child(popup)
            # Adding a legend to the map            
            legend_html =   '''
                    <div style="position: fixed; 
                                bottom: 100px; left: 50px; width: 120px; height: 90px; 
                                border:2px solid grey; z-index:9999; font-size:12px;
                                "
                                >
                                <b>
                                <font color="red">
                                &nbsp;                             
                                Legend
                                </font>
                                </b>
                                <br>
                                     <img 
                                         src="%s" alt="weather" height="40" width="40"
                                     />
                                      <b> <font color="green">
                                      &nbsp; %s &nbsp;
                                      </font>
                                      </b?
                                      <i 
                                          class="icon" style="color:red">
                                      </i>
                                <br>
                                  
                    </div>
                    ''' %(icon_url,weather)

            # Create and save the map
            maps.get_root().html.add_child(folium.Element(legend_html))        
            maps.save("C://Users//shaya//Desktop//Weather_map_data//"+city+"_"+last_timestamp_date.replace(":","_")+".html")



# Use this thread to open latest weather map and display map in window (should show last image as per last time stamp)
def thread_for_latest_weather_map(locations):
    '''
        In this function we take longitude and latitude of each city (location) and save its latest
        weather forecast map in a folder
    '''
    # Initialize MongoDB client running on localhost
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    for city in city_names:
        # Find the last record for each city as latest map record
        db = client.weather_data
        cursor = list(db['{}'.format(city)].find().sort([('_id', -1)]).limit(1))
        
        location = locations[city]
        maps = folium.Map(location=[location.latitude, location.longitude],tiles='cartodbdark_matter', zoom_start=8,
                   attr="<a href=https://endless-sky.github.io/>Endless Sky</a>")
        weather = str(cursor[0]["data"]['weather'][0]['description'])
        last_timestamp_date = str(cursor[0]["data"]['dt_txt'])
        temperature = str(round(float((cursor[0]["data"]["main"]["temp"] - 273.15)*(9/5)+32),2))
        icon = cursor[0]["data"]['weather'][0]['icon']   
        
        icon_url = "http://openweathermap.org/img/wn/"+icon+"@2x.png"

        icon = folium.features.CustomIcon(icon_url,
                                          icon_size=(100, 100),
                                          icon_anchor=(22, 94),
                                          popup_anchor=(-3, -76))

        # Subtracting values just to adjust the marker
        #marker = folium.Marker(location=[location.latitude-0.03, location.longitude-0.12], icon=icon, popup="Temperature is "+temperature+"F")
        marker = folium.Marker(location=[location.latitude-0.03, location.longitude-0.12], icon=icon, popup="Temperature is "+temperature+"F", html = '<div style="font-size:12pt">%s F</div>'%temperature)

#        folium.TileLayer('cartodbdark_matter').add_to(maps)
        maps.add_child(marker)
        maps.add_child(folium.Popup(temperature))
        legend_html =   '''
                <div style="position: fixed; 
                            bottom: 100px; left: 50px; width: 120px; height: 90px; 
                            border:2px solid grey; z-index:9999; font-size:12px;
                            "
                            >
                            <b>
                            <font color="red">
                            &nbsp;                             
                            Legend
                            </font>
                            </b>
                            <br>
                                 <img 
                                     src="%s" alt="weather" height="40" width="40"
                                 />
                                  <b> <font color="green">
                                  &nbsp; %s &nbsp;
                                  </font>
                                  </b?
                                  <i 
                                      class="icon" style="color:red">
                                  </i>
                            <br>
                </div>
                ''' %(icon_url,weather)
        maps.get_root().html.add_child(folium.Element(legend_html))        
        maps.save("C://Users//shaya//Desktop//Weather_map_data//Latest_weather_data//"+city+"_"+last_timestamp_date.replace(":","_")+"_latest_weather.html")


def thread_for_plotting_forecast_data():
    '''
        In this method, we plot the forecast history for each city by taking
        all its weather data from database and save the plot in a folder
    '''
    
    temperature_data_timestamps = []
    temperatures = {}
    date_times = []
    first_time=True
    # Initialize MongoDB client running on localhost
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    
    for city in city_names:
        temperatures[city] = []
    # Get all temperature data w.r.t. date and time from database
    with client:
        db = client.weather_data
        for city in city_names:
            data = db['{}'.format(city)].find({})
            for record in data:
                temperatures[city].append(record["data"]["main"]["temp"])
                if first_time:
                    date_times.append(record["data"]["dt_txt"])
            first_time=False

    # Plot the weather forecast for each city
    for city in city_names:
        plt.figure(figsize=(16,16))
        plt.xticks(rotation=90,fontsize=10)
        plt.title("Temperature forecast for "+str(city),fontsize=20)
        plt.xlabel("Date and Time",fontsize=12)
        plt.ylabel("Temperature (F)",fontsize=12)
        sns.lineplot(date_times, temperatures[city],zorder=2)
        plt.savefig("C://Users//shaya//Desktop//Weather_map_data//Plots//"+city+".png")
        plt.close()


if __name__ == "__main__":
    locations = {}
    
    # Get latitude and longitude of cities for which we want to forecast weather
    for city in city_names:
        locations[city] = geolocator.geocode(city)
        
    while 1:
        try:
            t1 = threading.Thread(target = lambda : thread_for_5_days_3_hour_forecast(), name='t1')
            t1.setDaemon(True)
            t2 = threading.Thread(target = lambda : thread_for_weather_maps(locations), name='t2')
            t2.setDaemon(True)
            t3 = threading.Thread(target = lambda : thread_for_latest_weather_map(locations), name='t3')
            t3.setDaemon(True)
            t4 = threading.Thread(target = lambda : thread_for_plotting_forecast_data(), name='t4')
            t4.setDaemon(True)
  
            t1.start()
            t1.join()
            t2.start()
            t2.join()
            t3.start()
            t3.join()
            t4.start()
            t4.join()
            time.sleep(refresh_frequency) 

        except Exception as e:
            print(e)
