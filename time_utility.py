from datetime import datetime
from datetime import date
from dotenv import dotenv_values
import requests
import math
import calendar
import utils


# split up the current time and format for use when we craft the text
def get_time():
    now = datetime.now().time()
    time_format = str(now).split(':')
    hour = int(time_format[0])
    am_pm = "am" if hour < 12 else "pm"  # determine AM or PM

    hour = hour % 12  # get rid of 24 hour time, make it 12 hour

    if hour == 0:  # normalize hour 0 to 12am
        hour = 12

    hour = str(hour)

    my_time = hour + ":" + time_format[1]

    seconds = int(math.floor(float(time_format[2])))

    return my_time, hour, am_pm, seconds, int(time_format[0]), int(time_format[1])  # return all the pieces we need


def get_day():
    return calendar.day_name[date.today().weekday()]  # day of week


def get_date():
    today = date.today()
    return today.strftime("%B %-d")  # nicely formatted month and day


def update_weather():
    url = dotenv_values(".env")["WEATHER_URL"]  # load weather URL from .env file

    response = requests.get(url)
    data = response.json()

    utils.forecast = data["weather"][0][
        "main"]  # format the pieces we want for our clock, short forecast, temp, real feel, and wind speed
    utils.temp = int(round(data["main"]["temp"]))
    utils.real_feel = int(round(data["main"]["feels_like"]))
    utils.wind = str(round(float(data["wind"]["speed"]), 1)) + " mph"

    if "Thunder" in utils.forecast:  # thunderstorms does not fit on the matrix, so i changed the shorthand
        utils.forecast = "T-Storms"
