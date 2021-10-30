from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

import drawing
from basic_commands import *
from text_handler import *
from emoji import emojize
from drawing import *
import time_utility
import text_handler
import utils
import logging
import threading
import asyncio
import os


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def button_generation(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    # generate inline keyboards for all the buttons in the /buttons command

    clock_controls_keyboard = [
        [
            InlineKeyboardButton("Override On", callback_data='on'),
            InlineKeyboardButton("Override Off", callback_data='off')
        ],
        [
            InlineKeyboardButton("Normalize Settings", callback_data='normalize')
        ]
    ]

    color_keyboard = [
        [
            InlineKeyboardButton("Night Lights", callback_data='red'),
            InlineKeyboardButton("Day Lights", callback_data='color')
        ],
        [
            InlineKeyboardButton("Change Clock Colors", callback_data='generate_clock_colors')
        ]
    ]

    text_controls_keyboard = [[
        InlineKeyboardButton("Font Size", callback_data='generate_font_size'),
        InlineKeyboardButton("Text Color", callback_data='generate_text_color_keyboard'),
        InlineKeyboardButton("Clear Text", callback_data='cleartext')
    ]]

    image_controls_keyboard = [
        [
            InlineKeyboardButton("Full Image", callback_data='full_image'),
            InlineKeyboardButton("Background Image", callback_data='background_image')
        ],
        [
            InlineKeyboardButton("Remove Image", callback_data='clearimage'),
            InlineKeyboardButton("Matrix Background Color", callback_data='generate_background_color_keyboard')
        ]
    ]

    system_keyboard = [
        [
            InlineKeyboardButton("Canvas Mode On", callback_data='canvas_mode_on'),
            InlineKeyboardButton("Canvas Mode Off", callback_data='canvas_mode_off')
        ],
        [
            InlineKeyboardButton("Ping", callback_data='ping'), InlineKeyboardButton("IP", callback_data='ip')
        ]
    ]

    update.message.reply_text(emojize(':mantelpiece_clock:') + " Clock Controls " + emojize(":mantelpiece_clock:"),
                              reply_markup=InlineKeyboardMarkup(clock_controls_keyboard))

    update.message.reply_text(emojize(':night_with_stars:') + " Color Control " + emojize(":night_with_stars:"),
                              reply_markup=InlineKeyboardMarkup(color_keyboard))

    update.message.reply_text(emojize(':pencil:') + " Text Controls " + emojize(":pencil:"),
                              reply_markup=InlineKeyboardMarkup(text_controls_keyboard))

    update.message.reply_text(emojize(':framed_picture:') + " Image Controls " + emojize(":framed_picture:"),
                              reply_markup=InlineKeyboardMarkup(image_controls_keyboard))

    update.message.reply_text(emojize(':robot:') + " System Controls " + emojize(":robot:"),
                              reply_markup=InlineKeyboardMarkup(system_keyboard))


def buttons(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = str(query.data)

    if data.startswith("color_"):
        update.callback_query.delete_message()
        utils.nonstandard_colors = True
        utils.update_board = True

        if utils.color_keyboard == ColorKeyboards.TEXT_COLOR:
            utils.text_color = utils.parse_color(data[6:])
        elif utils.color_keyboard == ColorKeyboards.BACKGROUND_COLOR:
            utils.background_color = utils.parse_color(data[6:])
        elif utils.color_keyboard == ColorKeyboards.DATE_COLOR:
            utils.date_color = utils.parse_color(data[6:])
        elif utils.color_keyboard == ColorKeyboards.TIME_COLOR:
            utils.time_color = utils.parse_color(data[6:])
        else:
            utils.weather_color = utils.parse_color(data[6:])

        return

    if "ip" in data:
        query.message.reply_text("Raspberry PI IP: " + utils.get_ip())
    elif "ping" in data:
        query.message.reply_text("Bot is working correctly.")
    elif "generate_font_size" in data:
        text_controls_keyboard = [[
            InlineKeyboardButton("Small", callback_data='small'),
            InlineKeyboardButton("Medium", callback_data='medium'),
            InlineKeyboardButton("Large", callback_data='large')
        ]]

        context.bot.send_message(update.effective_chat.id, emojize(':pencil:') + " Font Size " + emojize(":pencil:"),
                                 reply_markup=InlineKeyboardMarkup(text_controls_keyboard))
    elif "generate_clock_colors" in data:
        clock_controls_keyboard = [
            [
                InlineKeyboardButton("Date Color", callback_data='generate_date_color_keyboard'),
                InlineKeyboardButton("Time Color", callback_data='generate_time_color_keyboard'),
                InlineKeyboardButton("Weather Color", callback_data='generate_weather_color_keyboard')
            ],
            [
                InlineKeyboardButton("Cancel Color Change", callback_data='cancel')
            ]
        ]

        context.bot.send_message(update.effective_chat.id, emojize(':alarm_clock:') + " Clock Colors " +
                                 emojize(":alarm_clock:"), reply_markup=InlineKeyboardMarkup(clock_controls_keyboard))
    elif "generate_text_color_keyboard" in data:
        utils.color_keyboard = ColorKeyboards.TEXT_COLOR
        generate_color_keyboard(update, context)
    elif "generate_background_color_keyboard" in data:
        utils.color_keyboard = ColorKeyboards.BACKGROUND_COLOR
        generate_color_keyboard(update, context)
    elif "generate_date_color_keyboard" in data:
        update.callback_query.delete_message()
        utils.color_keyboard = ColorKeyboards.DATE_COLOR
        generate_color_keyboard(update, context)
    elif "generate_time_color_keyboard" in data:
        update.callback_query.delete_message()
        utils.color_keyboard = ColorKeyboards.TIME_COLOR
        generate_color_keyboard(update, context)
    elif "generate_weather_color_keyboard" in data:
        update.callback_query.delete_message()
        utils.color_keyboard = ColorKeyboards.WEATHER_COLOR
        generate_color_keyboard(update, context)
    elif "canvas_mode_on" in data:
        utils.update_board = True
        utils.canvas_mode = True
    elif "canvas_mode_off" in data:
        utils.update_board = True
        utils.canvas_mode = False
    elif "normalize" in data:   # set everything to defaults
        utils.override_red = False
        utils.override_color = False
        utils.override_on = False
        utils.show_text = 0
        utils.show_image = 0
        utils.image = None
        utils.text_lines = []
        utils.update_board = True
        utils.background_color = graphics.Color(0, 0, 0)
        utils.canvas_mode = False
    elif "custom_color" in data:
        update.callback_query.delete_message()

        # THIS IS FOR TESTING PURPOSES BEFORE FULL DRAWINGS IMPLEMENTATIOn
        # utils.drawings.append(CircleDrawing(0, 0, 10, "red"))
        # utils.drawings.append(RectangleDrawing(20, 20, 40, 35, 2, "green"))
        # utils.drawings.append(LineDrawing(50, 5, 55, 62, "yellow"))
        # utils.drawings.append(AreaDrawing(35, 8, 55, 15, "blue"))

        context.bot.send_message(update.effective_chat.id, "To use a custom color send /color [red] [green] [blue]")
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
        utils.canvas_mode = False
    elif "off" in data:
        utils.override_off = True
        utils.override_on = False
        utils.update_board = True
    elif "cleartext" in data:
        utils.show_text = 0
        utils.text_lines = []
        utils.update_board = True
    elif "clearimage" in data:
        utils.show_image = 0
        utils.image = None
        utils.update_board = True
    elif "small" in data:
        update.callback_query.delete_message()
        utils.font_size = 0
        text_handler.parse_text(utils.last_text_input)
        utils.update_board = True
    elif "medium" in data:
        update.callback_query.delete_message()
        utils.font_size = 1
        text_handler.parse_text(utils.last_text_input)
        utils.update_board = True
    elif "large" in data:
        update.callback_query.delete_message()
        utils.font_size = 2
        text_handler.parse_text(utils.last_text_input)
        utils.update_board = True
    elif "cancel" in data:
        update.callback_query.delete_message()
    elif "background_image" in data:
        utils.show_image = 1

        if utils.image is not None:
            utils.update_board = True
    elif "full_image" in data:
        utils.show_image = 2
        utils.canvas_mode = True

        if utils.image is not None:
            utils.update_board = True


def generate_color_keyboard(update: Update, context: CallbackContext) -> None:
    colors_keyboard = [
        [
            InlineKeyboardButton("Red", callback_data='color_red'),
            InlineKeyboardButton("Orange", callback_data='color_orange'),
            InlineKeyboardButton("Yellow", callback_data='color_yellow'),
            InlineKeyboardButton("Green", callback_data='color_green')
        ],
        [
            InlineKeyboardButton("Blue", callback_data='color_blue'),
            InlineKeyboardButton("Purple", callback_data='color_purple'),
            InlineKeyboardButton("Pink", callback_data='color_pink'),
            InlineKeyboardButton("Brown", callback_data='color_brown')
        ],
        [
            InlineKeyboardButton("White", callback_data='color_white'),
            InlineKeyboardButton("Gray", callback_data='color_gray'),
            InlineKeyboardButton("Black", callback_data='color_black'),
            InlineKeyboardButton("Custom", callback_data='custom_color')
        ],
        [
            InlineKeyboardButton("Cancel Color Change", callback_data='cancel')
        ]
    ]

    context.bot.send_message(update.effective_chat.id, emojize(':artist_palette:') + " Colors " + emojize(":artist_palette:"),
                             reply_markup=InlineKeyboardMarkup(colors_keyboard))


# event handler for if a picture is sent to chat
def poll_image(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    file = context.bot.get_file(update.message.photo[-1].file_id)       # grab sent file

    utils.image = utils.parse_image(file)                               # save file and update variables for display


async def update_clock():
    # off screen canvas to swap with
    offscreen_canvas = matrix.CreateFrameCanvas()
    
    while True:
        if utils.kill_program:
            return

        # grab current time
        now = time_utility.get_time()

        # as long as we are not using non standard colors to override
        # color switch time, currently red between midnight and 11am, normal day colors every other time
        # also clears the overrides at this time so they do not need to be manually reset
        if not utils.nonstandard_colors:
            if (now[4] == 0 and now[5] == 0) or utils.override_red:
                swap_color_defaults(True)
                utils.override_red = False
            elif (now[4] == 11 and now[5] == 0) or utils.override_color:
                swap_color_defaults(False)
                utils.override_color = False
            elif now[4] == 11 and now[5] == 0:
                utils.override_on = False
                utils.override_off = False

        current_time = now[0]

        # update weather every 5 minutes (to prevent exceeding the query limit for open weather api)
        if (current_time.endswith("0") or current_time.endswith("5")) and now[3] == 0:
            time_utility.update_weather()

        # make sure we update if we are at 0 seconds on the time (minute changed) and we do not have full screen text or an image
        if now[3] == 0 and utils.show_text < 2 and utils.show_image < 2:
            utils.update_board = True

        # if theres no override and we are in active hours
        if not utils.override_off and ((now[4] >= 11 or now[4] < 3) or utils.override_on):
            if utils.update_board:  # only update if we need to push something new (reduces flicker)
                # add background color
                offscreen_canvas.Fill(utils.background_color.red, utils.background_color.green,
                                      utils.background_color.blue)

                if utils.show_image > 0 and utils.image is not None:  # always show the image before going further if we have one
                    offscreen_canvas.SetImage(utils.image.convert('RGB'))

                position = ((64 - (len(current_time) * 8)) / 2) - 6  # determine central positioning for the date and time lines
                position2 = position + (len(current_time) * 8)

                show_text = utils.show_text
                text_color = utils.text_color

                if show_text < 2 and utils.show_image < 2 and not utils.canvas_mode:  # no image, lets show the day, date, and time
                    day = time_utility.get_day()
                    date = time_utility.get_date()

                    graphics.DrawText(offscreen_canvas, font_small, ((64 - len(day * 5)) / 2), 8, utils.date_color,
                                      day)
                    graphics.DrawText(offscreen_canvas, font_small, ((64 - len(date * 5)) / 2), 16, utils.date_color,
                                      date)
                    graphics.DrawText(offscreen_canvas, font_time, position, 29, utils.time_color, current_time)
                    graphics.DrawText(offscreen_canvas, font_medium, position2, 29, utils.time_color, now[2])

                if show_text == 0 and utils.show_image < 2 and not utils.canvas_mode:  # no text or image at all, lets show the weather
                    temp = utils.temp
                    forecast = utils.forecast
                    wind = utils.wind
                    real_feel = utils.real_feel

                    weather_top = str(temp) + "F   " + str(real_feel) + "F"

                    graphics.DrawText(offscreen_canvas, font_medium, ((64 - len(weather_top * 6)) / 2), 42,
                                      utils.weather_color, weather_top)
                    graphics.DrawText(offscreen_canvas, font_medium, ((64 - len(forecast * 6)) / 2), 50,
                                      utils.weather_color, forecast)
                    graphics.DrawText(offscreen_canvas, font_medium, ((64 - len(wind * 6)) / 2), 60,
                                      utils.weather_color, wind)

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

                # WE ARE GOING TO START DRAWING HERE
                for _ in range(len(utils.drawings)):
                    current_drawing = utils.drawings[_]

                    if type(current_drawing) == CircleDrawing:
                        graphics.DrawCircle(offscreen_canvas, current_drawing.x, current_drawing.y, current_drawing.radius,
                                            utils.parse_color(current_drawing.color))
                    elif type(current_drawing) == RectangleDrawing:
                        for offset in range(int(current_drawing.thickness)):
                            graphics.DrawLine(offscreen_canvas, current_drawing.x1, current_drawing.y1 + offset,
                                              current_drawing.x2, current_drawing.y1 + offset,
                                              utils.parse_color(current_drawing.color))
                            graphics.DrawLine(offscreen_canvas, current_drawing.x2 - offset, current_drawing.y1,
                                              current_drawing.x2 - offset, current_drawing.y2,
                                              utils.parse_color(current_drawing.color))
                            graphics.DrawLine(offscreen_canvas, current_drawing.x1, current_drawing.y2 - offset,
                                              current_drawing.x2, current_drawing.y2 - offset,
                                              utils.parse_color(current_drawing.color))
                            graphics.DrawLine(offscreen_canvas, current_drawing.x1 + offset, current_drawing.y1,
                                              current_drawing.x1 + offset, current_drawing.y2,
                                              utils.parse_color(current_drawing.color))
                    elif type(current_drawing) == LineDrawing:
                        graphics.DrawLine(offscreen_canvas, current_drawing.x1, current_drawing.y1, current_drawing.x2,
                                          current_drawing.y2, utils.parse_color(current_drawing.color))
                    elif type(current_drawing) == AreaDrawing:
                        for x in range(current_drawing.x1, current_drawing.x2):
                            for y in range(current_drawing.y1, current_drawing.y2):
                                color = utils.parse_color(current_drawing.color)
                                matrix.SetPixel(x, y, color.red, color.green, color.blue)
                    elif type(current_drawing) == BackgroundDrawing:
                        color = utils.parse_color(current_drawing.color)
                        offscreen_canvas.Fill(color.red, color.green, color.blue)
                    elif type(current_drawing) == TextDrawing:
                        print("NOT IMPLEMENTED YET")

                offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                offscreen_canvas.Clear()
                utils.update_board = False  # turn off update to prevent flicker
        else:
            if utils.update_board:
                matrix.Clear()

        await asyncio.sleep(1.0)


def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update_clock())


def main() -> None:
    updater = Updater(os.environ["API_KEY"])    # load bot API token environment variables

    updater.dispatcher.add_handler(CallbackQueryHandler(buttons))   # callback listener for the buttons
    updater.dispatcher.add_handler(CommandHandler('help', help_command))        # declare the commands
    updater.dispatcher.add_handler(CommandHandler('buttons', button_generation))
    updater.dispatcher.add_handler(CommandHandler('ping', ping))
    updater.dispatcher.add_handler(CommandHandler('ip', ip))
    updater.dispatcher.add_handler(CommandHandler('os', system_command))
    updater.dispatcher.add_handler(CommandHandler('kill', kill_command))
    updater.dispatcher.add_handler(CommandHandler('text', text))
    updater.dispatcher.add_handler(CommandHandler('textf', text))
    updater.dispatcher.add_handler(CommandHandler('color', color_command))

    updater.dispatcher.add_handler(MessageHandler(Filters.photo, poll_image))

    if 0 <= time_utility.get_time()[4] <= 11:    # if you start the clock in inactive hours, lets automatically set it to red
        utils.override_red = True

    # start the bot
    updater.start_polling(poll_interval=0.25)

    # begin the clock update listener
    time_utility.update_weather()

    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=loop_in_thread, args=(loop,))
    thread.start()

    # update_clock()

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
