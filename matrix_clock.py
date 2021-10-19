from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from emoji import emojize
from datetime import datetime
from datetime import date
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from dotenv import dotenv_values
import requests
import logging
import threading
import calendar
import math
import sys
import socket
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

def button_generation(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    # generate inline keyboards for all the buttons in the /buttons command

    clock_keyboard = [
        [
            InlineKeyboardButton("Override On", callback_data='on'),
            InlineKeyboardButton("Override Off", callback_data='off')
        ],
        [
            InlineKeyboardButton("Remove Text", callback_data='cleartext'),
            InlineKeyboardButton("Remove Image", callback_data='clearimage')
        ]
    ]

    color_keyboard = [[
        InlineKeyboardButton("Night Lights", callback_data='red'),
        InlineKeyboardButton("Day Lights", callback_data='color')
    ]]

    system_keyboard = [[
        InlineKeyboardButton("Ping", callback_data='ping'), InlineKeyboardButton("IP", callback_data='ip'),
        InlineKeyboardButton("Normalize", callback_data='normalize')
    ]]

    update.message.reply_text(emojize(':alarm_clock:') + " Clock Controls " + emojize(":alarm_clock:"),
                              reply_markup=InlineKeyboardMarkup(clock_keyboard))

    update.message.reply_text(emojize(':night_with_stars:') + " Color Control " + emojize(":night_with_stars:"),
                              reply_markup=InlineKeyboardMarkup(color_keyboard))

    update.message.reply_text(emojize(':robot:') + " System Controls " + emojize(":robot:"),
                              reply_markup=InlineKeyboardMarkup(system_keyboard))


def buttons(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = str(query.data)

    # grab global variables for updates
    global override_red
    global override_color
    global override_on
    global override_off
    global show_text
    global show_image
    global text_lines
    global update_board

    if "ip" in data:
        query.message.reply_text("Raspberry PI IP: " + get_ip())
    elif "ping" in data:
        query.message.reply_text("Bot is working correctly.")
    elif "normalize" in data:   # set everything to defaults
        override_red = False
        override_color = False
        override_on = False
        show_text = 0
        show_image = False
        text_lines = []
        update_board = True
    elif "red" in data:         # make sure conflicting variables are set to the opposite
        override_red = True
        override_color = False
        update_board = True
    elif "color" in data:
        override_color = True
        override_red = False
        update_board = True
    elif "on" in data:
        override_on = True
        override_off = False
        update_board = True
    elif "off" in data:
        override_off = True
        override_on = False
        update_board = True
    elif "cleartext" in data:
        show_text = 0
        text_lines = []
        update_board = True
    elif "clearimage" in data:
        show_image = False
        update_board = True


def system_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):        # ensure that we are authenticating for each command
        return

    text = update.message.text.replace("/os ", "")
    os.system(text)


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    update.message.reply_text("Use /buttons to generate the keyboard.\nUse /ping to ping the bot.\nUse /ip to view "
                              "the computer IP address.\nUse /os to run a system command.\nUse /text [text] to set text for the matrix.\n"
                              "Send an image to display an image on the matrix.")


def text(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    string = update.message.text.replace("/text ", "")      # catch text for bottom half and full screen
    string = string.replace("/textf ", "")

    global text_lines
    global show_text
    global update_board

    text_lines = []
    current_line = 0
    update_board = True

    show_text = 2 if "textf" in update.message.text else 1      # 3 part variable, 0 is no text, 1 is half, 2 is full

    if "|" not in string:           # pipe is newline character
        split = string.split(" ")

        for i in range(0, len(split)):
            if current_line >= len(text_lines):     # check if new line is greater than the length, append it to list if so for later reference
                text_lines.append(split[i])
            elif (len(text_lines[current_line]) + len(split[i]) + 1) <= 10:     # if we can fit in more words, add them on
                text_lines[current_line] = text_lines[current_line] + " " + split[i]
            else:           # we are out of space, create a new line
                current_line += 1
                text_lines.append(split[i])
    else:
        split = string.split("|")       # override the natural split using new line

        for i in range(0, len(split)):
            text_lines.append(split[i][0:10])       # grab only the first 10 characters of each line, thats as many as we can fit


def kill_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    global kill_program     # hard kill command if the program needs to be shut down
    kill_program = True

    sys.exit(0)


def ping(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    update.message.reply_text("Bot is working correctly.")


def ip(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    update.message.reply_text("Raspberry PI IP: " + get_ip())


def set_text_color(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    global text_color
    global update_board

    update_board = True

    color = update.message.text

    if len(update.message.text.replace("/textc ", "").split(" ")) == 3:     # custom rgb values, split at spaces in message
        rgb = update.message.text.replace("/textc ", "").split(" ")
        text_color = graphics.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        return

    if "red" in color:      # hard coded colors that can be used as a shortcut
        text_color = graphics.Color(128, 0, 0)
    if "orange" in color:
        text_color = graphics.Color(253, 88, 0)
    elif "yellow" in color:
        text_color = graphics.Color(255, 228, 0)
    elif "green" in color:
        text_color = graphics.Color(0, 160, 0)
    elif "blue" in color:
        text_color = graphics.Color(0, 64, 255)
    elif "purple" in color:
        text_color = graphics.Color(128, 0, 128)
    elif "pink" in color:
        text_color = graphics.Color(228, 0, 228)
    elif "brown" in color:
        text_color = graphics.Color(101, 67, 33)
    elif "white" in color:
        text_color = graphics.Color(255, 255, 255)
    elif "gray" in color:
        text_color = graphics.Color(128, 128, 128)
    elif "black" in color:
        text_color = graphics.Color(0, 0, 0)


def poll_image(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    file = context.bot.get_file(update.message.photo[-1].file_id)       # grab sent file

    imported = Image.open(BytesIO(file.download_as_bytearray()))        # convert to byte array to prevent saving locally
    imported = imported.resize((64, 64), Image.ANTIALIAS)               # resize to 64x64 for the 64x64 matrix

    global image

    image = Image.new(mode='RGB', size=(128, 32))                       # matrix unfortunately does not read in square, create long image so it reads as a line

    region1 = imported.crop((0, 0, 64, 32))                             # copy top half into the left half of long image
    region2 = imported.crop((0, 32, 64, 64))                            # copy bottom half into the right half of long image

    image.paste(region1, (0, 0, 64, 32))                                # paste segments
    image.paste(region2, (64, 0, 128, 32))

    global show_image                                                   # update variable to show
    show_image = True

    global update_board
    update_board = True


# REFERENCED: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_ip():
    return [l for l in (
        [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
            [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
             [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]


# check authorized user, pretty much make sure its my user name because i do not want anyone else using the bot
def authorized(update: Update) -> bool:
    if update.message.from_user.username != dotenv_values(".env")["AUTHORIZED_USER"]:
        print("!!! LOG-IN ATTEMPT !!!\nUsername: " + update.message.from_user.username)
        update.message.reply_text("You are not authorized to use this bot.")
        return False
    return True


# split up the current time and format for use when we craft the text
def get_time():
    now = datetime.now().time()
    time_format = str(now).split(':')
    hour = int(time_format[0])
    am_pm = "am" if hour < 12 else "pm"     # determine AM or PM

    hour = hour % 12                        # get rid of 24 hour time, make it 12 hour

    if hour == 0:                           # normalize hour 0 to 12am
        hour = 12

    hour = str(hour)

    my_time = hour + ":" + time_format[1]

    seconds = int(math.floor(float(time_format[2])))

    return my_time, hour, am_pm, seconds, int(time_format[0]), int(time_format[1])      # return all the pieces we need


def get_day():
    return calendar.day_name[date.today().weekday()]        # day of week


def get_date():
    today = date.today()
    return today.strftime("%B %-d")                         # nicely formatted month and day


def update_clock():
    global kill_program
    if kill_program:
        return

    threading.Timer(1.0, update_clock).start()  # run in a separate thread

    # CLOCK UPDATE FUNCTION, EVERYTHING ABOVE IS THREADING

    current_time = "fail"   # default value, will tell you visually if something went wrong

    # grabbing ALL the local variables
    global forecast
    global temp
    global real_feel
    global wind

    global override_red
    global override_color
    global override_on
    global override_off

    global red_color
    global purple_color
    global blue_color

    global update_weather

    global update_board

    global text_lines
    global text_color
    global show_text
    global show_image
    global image

    # grab current time
    now = get_time()

    # color switch time, currently red between midnight and 11am, normal day colors every other time
    # also clears the overrides at this time so they do not need to be manually reset
    if (now[4] == 0 and now[5] == 0) or override_red:
        red_color = graphics.Color(160, 0, 0)
        purple_color = graphics.Color(128, 0, 0)
        blue_color = graphics.Color(128, 0, 0)
        text_color = graphics.Color(128, 0, 0)
        override_red = False
    elif (now[4] == 11 and now[5] == 0) or override_color:
        red_color = graphics.Color(255, 0, 0)
        purple_color = graphics.Color(156, 0, 156)
        blue_color = graphics.Color(0, 64, 255)
        text_color = graphics.Color(0, 64, 255)
        override_color = False
    elif now[4] == 11 and now[5] == 0:
        override_on = False
        override_off = False

    # off screen canvas to swap with
    offscreen_canvas = matrix.CreateFrameCanvas()

    # simple check to make sure it does not glitch and update twice in a second
    if current_time != now[0]:
        current_time = now[0]

        if (current_time.endswith("0") or current_time.endswith("5")) and now[3] == 0:  # update weather every 5 minutes (to prevent exceeding the query limit for open weather api)
            update_weather = True

        if now[3] == 0 and show_text < 2 and not show_image:    # make sure we update if we are at 0 seconds on the time (minute changed) and we do not have full screen text or an image
            update_board = True

        if update_weather:
            url = dotenv_values(".env")["WEATHER_URL"]  # load weather URL from .env file

            response = requests.get(url)
            data = response.json()

            forecast = data["weather"][0]["main"]   # format the pieces we want for our clock, short forecast, temp, real feel, and wind speed
            temp = int(round(data["main"]["temp"]))
            real_feel = int(round(data["main"]["feels_like"]))
            wind = str(round(float(data["wind"]["speed"]), 1)) + " mph"

            if "Thunder" in forecast:       # thunderstorms does not fit on the matrix, so i changed the shorthand
                forecast = "T-Storms"

            update_weather = False

        if not override_off and ((now[4] >= 11 or now[4] < 3) or override_on):  # if theres no override and we are in active hours
            if show_image:      # always show the image before going further if we have one
                offscreen_canvas.SetImage(image.convert('RGB'))

            position = ((64 - (len(current_time) * 8)) / 2) - 6     # determine central positioning for the date and time lines
            position2 = position + (len(current_time) * 8)

            if update_board:            # only update if we need to push something new (reduces flicker)
                if show_text < 2:       # non full matrix text scenario
                    if not show_image:  # no image, lets show the day, date, and time
                        graphics.DrawText(offscreen_canvas, font_date, ((64 - len(get_day() * 5)) / 2), 8, purple_color, get_day())
                        graphics.DrawText(offscreen_canvas, font_date, ((64 - len(get_date() * 5)) / 2), 16, purple_color, get_date())
                        graphics.DrawText(offscreen_canvas, font, position, 29, red_color, current_time)
                        graphics.DrawText(offscreen_canvas, font_half, position2, 29, red_color, now[2])

                    if show_text == 0 and not show_image:   # no text or image at all, lets show the weather
                        weather_top = str(temp) + "F   " + str(real_feel) + "F"
                        graphics.DrawText(offscreen_canvas, font_half, ((64 - len(weather_top * 6)) / 2) + 64, 10, blue_color,
                                          weather_top)
                        graphics.DrawText(offscreen_canvas, font_half, ((64 - len(forecast * 6)) / 2) + 64, 18, blue_color,
                                          forecast)
                        graphics.DrawText(offscreen_canvas, font_half, ((64 - len(wind * 6)) / 2) + 64, 28, blue_color, wind)
                    else:   # there is either an image or text
                        if show_text == 1:  # lets show the text (will overlay with image (this is an intended feature))
                            if len(text_lines) >= 1:
                                graphics.DrawText(offscreen_canvas, font_half, ((64 - len(text_lines[0] * 6)) / 2) + 64, 9,
                                                  text_color, text_lines[0])

                            if len(text_lines) >= 2:
                                graphics.DrawText(offscreen_canvas, font_half, ((64 - len(text_lines[1] * 6)) / 2) + 64, 18,
                                                  text_color, text_lines[1])

                            if len(text_lines) >= 3:
                                graphics.DrawText(offscreen_canvas, font_half, ((64 - len(text_lines[2] * 6)) / 2) + 64, 27,
                                                  text_color, text_lines[2])
                else:   # we are full text, lets format and center all of the lines
                    if len(text_lines) >= 1:
                        graphics.DrawText(offscreen_canvas, font_half, ((64 - len(text_lines[0] * 6)) / 2), 9, text_color,
                                          text_lines[0])

                    if len(text_lines) >= 2:
                        graphics.DrawText(offscreen_canvas, font_half, ((64 - len(text_lines[1] * 6)) / 2), 18, text_color,
                                          text_lines[1])

                    if len(text_lines) >= 3:
                        graphics.DrawText(offscreen_canvas, font_half, ((64 - len(text_lines[2] * 6)) / 2), 27, text_color,
                                          text_lines[2])

                    if len(text_lines) >= 4:
                        graphics.DrawText(offscreen_canvas, font_half, ((64 - len(text_lines[3] * 6)) / 2) + 64, 9, text_color,
                                          text_lines[3])

                    if len(text_lines) >= 5:
                        graphics.DrawText(offscreen_canvas, font_half, ((64 - len(text_lines[4] * 6)) / 2) + 64, 18, text_color,
                                          text_lines[4])

                    if len(text_lines) >= 6:
                        graphics.DrawText(offscreen_canvas, font_half, ((64 - len(text_lines[5] * 6)) / 2) + 64, 27, text_color,
                                          text_lines[5])

    if update_board:    # only swap screen on update events
        matrix.SwapOnVSync(offscreen_canvas)

    update_board = False    # if there was an update, it would have already been covered so lets turn that off to prevent flicker


# declare field variables
kill_program = False

red_color = graphics.Color(255, 0, 0)
purple_color = graphics.Color(128, 0, 128)
blue_color = graphics.Color(0, 64, 255)

text_color = graphics.Color(0, 64, 255)

override_red = False
override_color = False
override_on = False
override_off = False

update_weather = True
forecast = "yeet"
temp = 0
real_feel = 0
wind = "0.0 mph"

update_board = True
text_lines = []
show_text = 0
show_image = False
image = None


def main() -> None:
    updater = Updater(dotenv_values(".env")["API_KEY"]) # load bot API token from .env file

    updater.dispatcher.add_handler(CallbackQueryHandler(buttons))   # callback listener for the buttons
    updater.dispatcher.add_handler(CommandHandler('help', help_command))        # declare the commands
    updater.dispatcher.add_handler(CommandHandler('buttons', button_generation))
    updater.dispatcher.add_handler(CommandHandler('ping', ping))
    updater.dispatcher.add_handler(CommandHandler('ip', ip))
    updater.dispatcher.add_handler(CommandHandler('os', system_command))
    updater.dispatcher.add_handler(CommandHandler('kill', kill_command))
    updater.dispatcher.add_handler(CommandHandler('text', text))
    updater.dispatcher.add_handler(CommandHandler('textf', text))
    updater.dispatcher.add_handler(CommandHandler('textc', set_text_color))

    updater.dispatcher.add_handler(MessageHandler(Filters.photo, poll_image))

    if 0 <= get_time()[4] <= 11:    # if you start the clock in inactive hours, lets automatically set it to red
        global override_red
        override_red = True

    # start the bot
    updater.start_polling()

    # begin the clock update listener
    update_clock()

    # run the bot until process ends
    updater.idle()


if __name__ == '__main__':
    options = RGBMatrixOptions()    # matrix set up options, API requires this to run first in a program
    options.rows = 32
    options.cols = 64
    options.chain_length = 2
    options.parallel = 1
    options.pwm_lsb_nanoseconds = 50
    options.brightness = 50
    options.pwm_dither_bits = 1
    options.hardware_mapping = 'adafruit-hat-pwm'

    matrix = RGBMatrix(options=options)

    font = graphics.Font()  # default fonts that are constantly referenced throughout
    font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/8x13B.bdf")

    font_half = graphics.Font()
    font_half.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/6x9.bdf")

    font_date = graphics.Font()
    font_date.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/5x8.bdf")

    main()      # go to the main function for bot setup
