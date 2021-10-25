from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from basic_commands import *
from text_handler import *
from emoji import emojize
import time_utility
import text_handler
import utils
import logging
import threading
import os


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


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

    font_keyboard = [[
        InlineKeyboardButton("Small", callback_data='small'), InlineKeyboardButton("Medium", callback_data='medium'),
        InlineKeyboardButton("Large", callback_data='large')
    ]]

    system_keyboard = [[
        InlineKeyboardButton("Ping", callback_data='ping'), InlineKeyboardButton("IP", callback_data='ip'),
        InlineKeyboardButton("Normalize", callback_data='normalize')
    ]]

    update.message.reply_text(emojize(':alarm_clock:') + " Clock Controls " + emojize(":alarm_clock:"),
                              reply_markup=InlineKeyboardMarkup(clock_keyboard))

    update.message.reply_text(emojize(':night_with_stars:') + " Color Control " + emojize(":night_with_stars:"),
                              reply_markup=InlineKeyboardMarkup(color_keyboard))

    update.message.reply_text(emojize(':pencil:') + " Font Size " + emojize(":pencil:"),
                              reply_markup=InlineKeyboardMarkup(font_keyboard))

    update.message.reply_text(emojize(':robot:') + " System Controls " + emojize(":robot:"),
                              reply_markup=InlineKeyboardMarkup(system_keyboard))


def buttons(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = str(query.data)

    if "ip" in data:
        query.message.reply_text("Raspberry PI IP: " + utils.get_ip())
    elif "ping" in data:
        query.message.reply_text("Bot is working correctly.")
    elif "normalize" in data:   # set everything to defaults
        utils.override_red = False
        utils.override_color = False
        utils.override_on = False
        utils.show_text = 0
        utils.show_image = False
        utils.text_lines = []
        utils.update_board = True
    elif "red" in data:         # make sure conflicting variables are set to the opposite
        utils.override_red = True
        utils.override_color = False
        utils.update_board = True
    elif "color" in data:
        utils.override_color = True
        utils.override_red = False
        utils.update_board = True
    elif "on" in data:
        utils.override_on = True
        utils.override_off = False
        utils.update_board = True
    elif "off" in data:
        utils.override_off = True
        utils.override_on = False
        utils.update_board = True
    elif "cleartext" in data:
        utils.show_text = 0
        utils.text_lines = []
        utils.update_board = True
    elif "clearimage" in data:
        utils.show_image = False
        utils.update_board = True
    elif "small" in data:
        utils.font_size = 0
        text_handler.parse_text(utils.last_text_input)
        utils.update_board = True
    elif "medium" in data:
        utils.font_size = 1
        text_handler.parse_text(utils.last_text_input)
        utils.update_board = True
    elif "large" in data:
        utils.font_size = 2
        text_handler.parse_text(utils.last_text_input)
        utils.update_board = True


# event handler for if a picture is sent to chat
def poll_image(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    file = context.bot.get_file(update.message.photo[-1].file_id)       # grab sent file

    utils.image = utils.parse_image(file)                               # save file and update variables for display
    utils.show_image = True
    utils.update_board = True


def update_clock():
    if utils.kill_program:
        return

    threading.Timer(1.0, update_clock).start()  # run in a separate thread

    # CLOCK UPDATE FUNCTION, EVERYTHING ABOVE IS THREADING

    current_time = "fail"   # default value, will tell you visually if something went wrong

    # grab current time
    now = time_utility.get_time()

    # color switch time, currently red between midnight and 11am, normal day colors every other time
    # also clears the overrides at this time so they do not need to be manually reset
    if (now[4] == 0 and now[5] == 0) or utils.override_red:
        swap_color_defaults(True)
        utils.override_red = False
    elif (now[4] == 11 and now[5] == 0) or utils.override_color:
        swap_color_defaults(False)
        utils.override_color = False
    elif now[4] == 11 and now[5] == 0:
        utils.override_on = False
        utils.override_off = False

    # off screen canvas to swap with
    offscreen_canvas = matrix.CreateFrameCanvas()

    current_time = now[0]

    # update weather every 5 minutes (to prevent exceeding the query limit for open weather api)
    if (current_time.endswith("0") or current_time.endswith("5")) and now[3] == 0:
        time_utility.update_weather()

    # make sure we update if we are at 0 seconds on the time (minute changed) and we do not have full screen text or an image
    if now[3] == 0 and utils.show_text < 2 and not utils.show_image:
        utils.update_board = True

    # if theres no override and we are in active hours
    if not utils.override_off and ((now[4] >= 11 or now[4] < 3) or utils.override_on):
        if utils.show_image:  # always show the image before going further if we have one
            offscreen_canvas.SetImage(utils.image.convert('RGB'))

        position = ((64 - (len(current_time) * 8)) / 2) - 6  # determine central positioning for the date and time lines
        position2 = position + (len(current_time) * 8)

        if utils.update_board:  # only update if we need to push something new (reduces flicker)
            show_text = utils.show_text
            text_color = utils.text_color

            if not utils.show_image and show_text < 2:  # no image, lets show the day, date, and time
                day = time_utility.get_day()
                date = time_utility.get_date()

                graphics.DrawText(offscreen_canvas, font_small, ((64 - len(day * 5)) / 2), 8, utils.purple_color,
                                  day)
                graphics.DrawText(offscreen_canvas, font_small, ((64 - len(date * 5)) / 2), 16, utils.purple_color,
                                  date)
                graphics.DrawText(offscreen_canvas, font_time, position, 29, utils.red_color, current_time)
                graphics.DrawText(offscreen_canvas, font_medium, position2, 29, utils.red_color, now[2])

            if show_text == 0 and not utils.show_image:  # no text or image at all, lets show the weather
                temp = utils.temp
                forecast = utils.forecast
                wind = utils.wind
                real_feel = utils.real_feel

                weather_top = str(temp) + "F   " + str(real_feel) + "F"

                graphics.DrawText(offscreen_canvas, font_medium, ((64 - len(weather_top * 6)) / 2), 42,
                                  utils.blue_color, weather_top)
                graphics.DrawText(offscreen_canvas, font_medium, ((64 - len(forecast * 6)) / 2), 50,
                                  utils.blue_color, forecast)
                graphics.DrawText(offscreen_canvas, font_medium, ((64 - len(wind * 6)) / 2), 60,
                                  utils.blue_color, wind)

            if show_text > 0:
                for line_of_text in utils.text_lines:
                    if utils.font_size == 0:
                        font = font_small
                    elif utils.font_size == 1:
                        font = font_medium
                    else:
                        font = font_large

                    positioning = line_of_text.parse_position()

                    graphics.DrawText(offscreen_canvas, font, positioning[0], positioning[1], text_color, line_of_text.line_text)

    if utils.update_board:    # only swap screen on update events
        matrix.SwapOnVSync(offscreen_canvas)
        utils.update_board = False    # turn off update to prevent flicker


def main() -> None:
    updater = Updater(os.environ["API_KEY"]) # load bot API token environment variables

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

    if 0 <= time_utility.get_time()[4] <= 11:    # if you start the clock in inactive hours, lets automatically set it to red
        utils.override_red = True

    # start the bot
    updater.start_polling(poll_interval=1.0)

    # begin the clock update listener
    time_utility.update_weather()
    update_clock()

    # run the bot until process ends
    updater.idle()


if __name__ == '__main__':
    options = RGBMatrixOptions()    # matrix set up options, API requires this to run first in a program
    options.rows = 64
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.pwm_lsb_nanoseconds = 50
    options.brightness = 50
    options.pwm_dither_bits = 1
    options.hardware_mapping = 'adafruit-hat-pwm'

    matrix = RGBMatrix(options=options)

    font_time = graphics.Font()  # default fonts that are constantly referenced throughout
    font_time.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/8x13B.bdf")

    font_large = graphics.Font()  # default fonts that are constantly referenced throughout
    font_large.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/8x13.bdf")

    font_medium = graphics.Font()
    font_medium.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/6x9.bdf")

    font_small = graphics.Font()
    font_small.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/5x8.bdf")

    main()      # go to the main function for bot setup
