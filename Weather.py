#!/usr/bin/env python3
# Module for getting weather updates, methods for updating, formatting, and displaying weather

import requests
import json
import datetime
import pytz
import threading
import time
import SonosUtils
import math

class UpdateWeather:

    def __init__(self, location_id = "5913490", auth_key_current = "1b2c8e00bfa16ce7a48f76c3570fd3a2",
                 auth_key_forecast = "3b90cad26425a346141a426741656660",
                 disp_lines=3, disp_width=22, fcst_period = 1, update_freq = 10, time_zone = "Canada/Mountain"):
        '''
        Gets weather update from openweathermap.org, methods for converting temperature to c and getting forecast

        :param location_id:         numeric location id for openweathermap.org API. default is Calgary
        :type location_id:          int ; 7 digits
        :param auth_key:            API access key
        :type auth_key:             str
        :param disp_lines:          number of lines in the display
        :type disp_lines:           int
        :param disp_width:          number of characters to fit weather info into
        :type disp_width:           int
        :param fcst_period:         number of hours to get the forecast for, in hours
        :type fcst_period:          int
        :param update_freq:         time between forecast updates in minutes
        :type: update_freq:         int
        '''

        self.location_id = location_id
        self.auth_key_current = auth_key_current
        self.aut_key_current = auth_key_forecast
        self.disp_lines = disp_lines
        self.disp_width = disp_width
        self.fcst_period = fcst_period
        self.update_freq = update_freq
        self.time_zone = time_zone
        # note openweathermap.org updates weather data every 10 minutes, no need to check more often than that.
        #set up thread to run weather update loop in
        weather_loop = threading.Thread(target=self.weather_update)
        weather_loop.start()
        # make dictionary to hold weather info, see description in weather_update
        self.weather_info = {"current":{"time":0,"desc":"","temp":0,"wind":0,"wind_dir":" "},
                             "forecast":{"time":0,"desc":"","temp":0,"wind":0,"wind_dir":" "}}

    def weather_update(self):
        '''

        loops every update_freq and gets updated current weather and forecast from openweathermap.org
        puts weather info into a nested dictionary called weather_info
                [current][forecast]
                    [time][desc][temp][wind][wind_dir] (for both current and forecast]
                where:
                time:  time of forecast
                desc:   short text description of weather
                temp:   temperature in Kelvin
                wind:   wind speed in m/sec
                wind_dir:   wind direction in compass degrees

        :param  timezone:   timezone offset from UTC in seconds
        :type timezone:     int
        '''

        while True:

            # make urls to get weather data. go to openweathermap.org for details
            current_url = "http://api.openweathermap.org/data/2.5/weather?id=" + \
                          self.location_id + "&appid=" + self.auth_key_current
            forecast_url = "http://api.openweathermap.org/data/2.5/forecast?id=" +\
                           self.location_id + "&appid=" + self.auth_key_forecast

            # get current weather data, json format
            current_json = requests.get(current_url).json()
            # get current weather time, put in weather_info
            current_time = datetime.datetime.fromtimestamp(current_json["dt"]).strftime('%Hh')
            self.weather_info["current"]["time"] = current_time
            self.weather_info["current"]["desc"] = current_json["weather"][0]["description"]
            self.weather_info["current"]["temp"] = round(current_json["main"]["temp"] - 273)
            self.weather_info["current"]["wind"] = round(current_json["wind"]["speed"] * 3.6)
            # get wind direction, have to convert from degrees to cardinal
            #   multiply by 3.6 to convert from m/sec to km/hr
            # get wind direction.  if wind speed is 0 then there is no wind direction in the json, if so make windspeed 0
            try:
                current_wind_deg = current_json["wind"]["dir"]
            except:
                current_wind_deg = 0
            # convert to cardinal
            self.weather_info["current"]["wind_dir"] = self.degrees_to_cardinal(deg=current_wind_deg)

            # get forecast json
            forecast_json = requests.get(forecast_url).json()
            # put forecast weather time, description, temperature and put in weather_info dictionary
            # get current time of forecast un unix utc format
            forecast_time_unix_utc = forecast_json["list"][self.fcst_period]["dt"]
            # convert timestamp into a python datetime object
            forecast_time = datetime.datetime.fromtimestamp(forecast_time_unix_utc)

            # add timezone information, so daylight savings time works properly
            forecast_time_local = pytz.timezone(self.time_zone).localize(forecast_time)

            print("**********getting forecast*******")
            print("forecast time:", forecast_time_local)
            #check to see if it is not dst, is so add 1 hour to the time
            # openweathermap.org gets dst backwards, in winter we have to add one hour to get the correct forecast time
            if self.is_not_dst():
                forecast_time_local =forecast_time_local + datetime.timedelta(hours=1)
                print ("adding one hour to adjust for no dst")
            forecast_time_hour = forecast_time_local.strftime('%H')
            print("just the hour: ", forecast_time_hour)
            # convert time to local and format and put into weather_info
            self.weather_info["forecast"]["time"] = forecast_time_hour

            # put forecast desc and temp into weather_info
            self.weather_info["forecast"]["desc"] = \
                forecast_json["list"][self.fcst_period]["weather"][0]["description"]
            self.weather_info["forecast"]["temp"] = \
                round(forecast_json["list"][self.fcst_period]["main"]["temp"] - 273)
            #   temperatures are in kelvin, subtract 273 to get celsius and round to one decimal place
            # get wind direction and speed
            self.weather_info["forecast"]["wind"] = round(forecast_json["list"][self.fcst_period]["wind"]["speed"] *3.6)
            fcst_wind_dir_deg = round(forecast_json["list"][self.fcst_period]["wind"]["deg"])
            fcst_wind_dir_arrows = self.degrees_to_arrows(deg=fcst_wind_dir_deg)
            fcst_wind_dir_card = self.degrees_to_cardinal(deg = fcst_wind_dir_deg)
            self.weather_info["forecast"]["wind_dir"] = fcst_wind_dir_card

            time.sleep(self.update_freq*60)

    def degrees_to_cardinal(self,deg = 0):
        '''
       converts degrees (360) to a cardinal direction
       several versions of cardinal commented out; divide by appropriate factor to get right direction
       ie for 8 cardinal directions divide degrees by 45, for 16 divide by 24
        '''
        # dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        #        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        # dirs = ["n","nne","ne","ene","e","ese","se","sse""s","ssw","sw","wsw", "w", "wnw","nw","nnw"]
        dirs = ["n", "ne", "e", "se","s", "sw", "w", "nw"]
        # make index for dirs_lc from degrees, divide by 45, subtract 1, round up - gives range of 0-7 for input of 0-360
        ix = int(round(deg / 51.4,0))
        # get the corresponding cardinal direction
        dir_card = dirs[ix]

        return dir_card

    def degrees_to_arrows(self, deg = 0):
        '''
        attempt to convert degrees into arrows
        :param deg:
        :type deg:
        :return:
        :rtype:
        '''
        # make list of unicode characters for the direction arrows
        dirs = ['\u2193','\u2199','\u2190','\u2196','\u2191','\u2197','\u2192','\u2198','\u2193']
        # make index for list based on 360 degrees, ie 45 degrees would be second item, NNE, arrow pointing down and to left
        ix = math.ceil((deg / 45)-1)
        #get the right arrow from the list
        dir_card = dirs[ix % 8]

        return dir_card


    def make_weather_disp(self,line_width = 26,cpu_temp = False):
        '''
        make strings to describe weather & time, split over desired lines
        :param weather:
        :type weather:
        :return:
        :rtype:
        '''

        if self.disp_lines == 3:
            lines = ["","",""]
            #first line will be date and time, plus cpu temperature (if cpu_temp = True
            if cpu_temp:
                # add cpu temperature to first line
                lines[0] = SonosUtils.center_text(time.strftime("%b %d %I:%M %p")
                                            + str(round(SonosUtils.get_cpu_temp()))+"c",line_width)
            else:
                lines[0] = SonosUtils.center_text(time.strftime("%b %d %I:%M %p"), line_width -2)
            #second line is the current weather
            lines[1] = SonosUtils.center_text(self.weather_info["current"]["desc"]+" " +
                                              str(self.weather_info["current"]["temp"]) + "c " +
                                              str(self.weather_info["current"]["wind"])+
                                              self.weather_info["current"]["wind_dir"],line_width)
            # third line is the forecast.
            # get description and truncate it to 12 characters (to fit display better)
            description_short = self.weather_info['forecast']['desc'][:12]
            #description_short = description[:12]
            lines[2] = SonosUtils.center_text(self.weather_info["forecast"]["time"] + "h " +
                                              description_short + " " +
                                              str(self.weather_info["forecast"]["temp"]) + "c " +
                                              str(self.weather_info["forecast"]["wind"]) +
                                              self.weather_info["forecast"]["wind_dir"],line_width)
        return lines


    def is_not_dst(self):

        """Determine whether or not Daylight Savings Time (DST)
        is currently in effect"""

        x = datetime.datetime(datetime.datetime.now().year, 1, 1, 0, 0, 0, tzinfo=pytz.timezone(self.time_zone))  # Jan 1 of this year
        y = datetime.datetime.now(pytz.timezone(self.time_zone))

        # if DST is in effect, their offsets will be different
        return not (y.utcoffset() == x.utcoffset())