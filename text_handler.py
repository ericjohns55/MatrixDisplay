from telegram import Update
from telegram.ext import CallbackContext
from rgbmatrix import graphics
from utils import authorized
import utils


def text(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    string = update.message.text.replace("/text ", "")      # catch text for bottom half and full screen
    string = string.replace("/textf ", "")

    utils.show_text = 2 if "textf" in update.message.text else 1      # 3 part variable, 0 is no text, 1 is half, 2 is full
    utils.update_board = True

    text_lines = []
    current_line = 0

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

    utils.text_lines = text_lines.copy()


def set_text_color(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    utils.update_board = True

    color = update.message.text

    if len(update.message.text.replace("/textc ", "").split(" ")) == 3:     # custom rgb values, split at spaces in message
        rgb = update.message.text.replace("/textc ", "").split(" ")
        utils.text_color = graphics.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        return

    if "red" in color:      # hard coded colors that can be used as a shortcut
        utils.text_color = graphics.Color(128, 0, 0)
    if "orange" in color:
        utils.text_color = graphics.Color(253, 88, 0)
    elif "yellow" in color:
        utils.text_color = graphics.Color(255, 228, 0)
    elif "green" in color:
        utils.text_color = graphics.Color(0, 160, 0)
    elif "blue" in color:
        utils.text_color = graphics.Color(0, 64, 255)
    elif "purple" in color:
        utils.text_color = graphics.Color(128, 0, 128)
    elif "pink" in color:
        utils.text_color = graphics.Color(228, 0, 228)
    elif "brown" in color:
        utils.text_color = graphics.Color(101, 67, 33)
    elif "white" in color:
        utils.text_color = graphics.Color(255, 255, 255)
    elif "gray" in color:
        utils.text_color = graphics.Color(128, 128, 128)
    elif "black" in color:
        utils.text_color = graphics.Color(0, 0, 0)


def swap_color_defaults(night: bool):
    if night:
        utils.red_color = graphics.Color(160, 0, 0)
        utils.purple_color = graphics.Color(128, 0, 0)
        utils.blue_color = graphics.Color(128, 0, 0)
        utils.text_color = graphics.Color(128, 0, 0)
    else:
        utils.red_color = graphics.Color(255, 0, 0)
        utils.purple_color = graphics.Color(156, 0, 156)
        utils.blue_color = graphics.Color(0, 64, 255)
        utils.text_color = graphics.Color(0, 64, 255)
