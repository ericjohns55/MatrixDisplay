# Eric Johns
# MatrixDisplay
# https://github.com/ericjohns55/MatrixDisplay/

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from datetime import datetime
import drawing
import asyncio
import threading
import bot_handler
import os

MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32

FONTS_FOLDER = "fonts"
DRAWINGS_FOLDER = "/home/pi/rpi-rgb-led-matrix/fonts"
BOT_API_KEY = "<your API key here>"


def get_time():
    now = datetime.now()

    hour = now.hour
    minute = now.minute
    second = now.second
    am_pm = "am" if hour < 12 else "pm"

    hour %= 12      # adjust to 12 hour format
    if hour == 0:
        hour = 12

    formatted = str(hour) + ":"

    if minute < 10:
        formatted += "0"

    formatted += str(minute) + am_pm

    return hour, minute, second, am_pm, formatted   # return all our time formatting options


async def update_matrix():
    offscreen_canvas = matrix.CreateFrameCanvas()

    while True:         # update only if an update is required OR there is a clock on board and the time just changed
        if bot_handler.screen_update_required or (bot_handler.contains_clock_drawing and get_time()[2] == 0):
            bot_handler.screen_update_required = False  # disable our need to update again

            # loop through all drawings and draw the individual ones using the data stored in the drawing classes
            for current_drawing in bot_handler.drawings_list:
                if type(current_drawing) == drawing.CircleDrawing:
                    graphics.DrawCircle(offscreen_canvas, current_drawing.x, current_drawing.y, current_drawing.radius, current_drawing.color)
                elif type(current_drawing) == drawing.RectangleDrawing:
                    for offset in range(int(current_drawing.thickness)):    # draw a bunch of lines for a rectangle with a thickness
                        graphics.DrawLine(offscreen_canvas, current_drawing.x1, current_drawing.y1 + offset,
                                          current_drawing.x2, current_drawing.y1 + offset,
                                          current_drawing.color)
                        graphics.DrawLine(offscreen_canvas, current_drawing.x2 - offset, current_drawing.y1,
                                          current_drawing.x2 - offset, current_drawing.y2,
                                          current_drawing.color)
                        graphics.DrawLine(offscreen_canvas, current_drawing.x1, current_drawing.y2 - offset,
                                          current_drawing.x2, current_drawing.y2 - offset,
                                          current_drawing.color)
                        graphics.DrawLine(offscreen_canvas, current_drawing.x1 + offset, current_drawing.y1,
                                          current_drawing.x1 + offset, current_drawing.y2,
                                          current_drawing.color)
                elif type(current_drawing) == drawing.LineDrawing:
                    graphics.DrawLine(offscreen_canvas, current_drawing.x1, current_drawing.y1, current_drawing.x2, current_drawing.y2,
                                      current_drawing.color)
                elif type(current_drawing) == drawing.FillDrawing:
                    for x in range(current_drawing.x1, current_drawing.x2):
                        for y in range(current_drawing.y1, current_drawing.y2):
                            color = current_drawing.color
                            offscreen_canvas.SetPixel(x, y, color.red, color.green, color.blue)
                elif type(current_drawing) == drawing.BackgroundDrawing:
                    color = current_drawing.color
                    offscreen_canvas.Fill(color.red, color.green, color.blue)
                elif type(current_drawing) == drawing.PictureDrawing:
                    offscreen_canvas.SetImage(current_drawing.image.convert('RGB'))
                elif type(current_drawing) == drawing.TextDrawing:
                    graphics.DrawText(offscreen_canvas, current_drawing.parse_font(), current_drawing.x, current_drawing.y,
                                      current_drawing.color, current_drawing.text)
                elif type(current_drawing) == drawing.ClockDrawing:
                    time_text = get_time()[4]

                    x_pos = current_drawing.x

                    if x_pos == -1: # center the text if we inputted the position as -1
                        x_pos = drawing.get_center_x(MATRIX_WIDTH, current_drawing.font, time_text)

                    graphics.DrawText(offscreen_canvas, current_drawing.parse_font(), x_pos, current_drawing.y,
                                      current_drawing.color, time_text)

            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)     # swap with an offscreen buffer to preserve resources
            offscreen_canvas.Clear()

        await asyncio.sleep(1.0)    # sleep for a second


def update_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update_matrix())


def main() -> None:
    updater = Updater(BOT_API_KEY)

    # load the commands
    updater.dispatcher.add_handler(CommandHandler("circle", bot_handler.circle_command))
    updater.dispatcher.add_handler(CommandHandler("c", bot_handler.circle_command))
    updater.dispatcher.add_handler(CommandHandler("rectangle", bot_handler.rectangle_command))
    updater.dispatcher.add_handler(CommandHandler("r", bot_handler.rectangle_command))
    updater.dispatcher.add_handler(CommandHandler("line", bot_handler.line_command))
    updater.dispatcher.add_handler(CommandHandler("l", bot_handler.line_command))
    updater.dispatcher.add_handler(CommandHandler("fill", bot_handler.fill_command))
    updater.dispatcher.add_handler(CommandHandler("f", bot_handler.fill_command))
    updater.dispatcher.add_handler(CommandHandler("background", bot_handler.background_command))
    updater.dispatcher.add_handler(CommandHandler("bg", bot_handler.background_command))
    updater.dispatcher.add_handler(CommandHandler("clock", bot_handler.clock_command))
    updater.dispatcher.add_handler(CommandHandler("text", bot_handler.text_command))
    updater.dispatcher.add_handler(CommandHandler("t", bot_handler.text_command))
    updater.dispatcher.add_handler(CommandHandler("toptext", bot_handler.top_text_command))
    updater.dispatcher.add_handler(CommandHandler("bottomtext", bot_handler.bottom_text_command))
    updater.dispatcher.add_handler(CommandHandler("textf", bot_handler.text_format_command))
    updater.dispatcher.add_handler(CommandHandler("clear", bot_handler.clear_command))
    updater.dispatcher.add_handler(CommandHandler("drawings", bot_handler.drawings_command))
    updater.dispatcher.add_handler(CommandHandler("swap", bot_handler.swap_command))
    updater.dispatcher.add_handler(CommandHandler("remove", bot_handler.remove_command))
    updater.dispatcher.add_handler(CommandHandler("save", bot_handler.save_command))
    updater.dispatcher.add_handler(CommandHandler("load", bot_handler.load_command))
    updater.dispatcher.add_handler(CommandHandler("list", bot_handler.list_command))
    updater.dispatcher.add_handler(CommandHandler("delete", bot_handler.delete_command))
    updater.dispatcher.add_handler(CommandHandler("buttons", bot_handler.buttons_command))

    # callback for uploading a picture
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, bot_handler.poll_image))

    # callback for the inline keyboard
    updater.dispatcher.add_handler(CallbackQueryHandler(bot_handler.keyboard_callback))

    updater.start_polling(poll_interval=0.25)

    # run the update method in a separate thread
    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=update_loop, args=(loop,))
    thread.start()

    print("Telegram bot loaded.\nRunning matrix loop...")

    updater.idle() # loop the bot forever

    return


if __name__ == '__main__':
    options = RGBMatrixOptions()    # matrix set up options, API requires this to run first in a program
    options.rows = MATRIX_HEIGHT    # change as you need
    options.cols = MATRIX_WIDTH
    options.pwm_lsb_nanoseconds = 130
    options.brightness = 50
    options.gpio_slowdown = 3
    options.hardware_mapping = 'adafruit-hat-pwm'

    matrix = RGBMatrix(options=options) # if more info is typed into the command line then we can find it

    if not os.path.exists(DRAWINGS_FOLDER):     # create a drawings folder for persistence
        os.mkdir(DRAWINGS_FOLDER)

    main()
