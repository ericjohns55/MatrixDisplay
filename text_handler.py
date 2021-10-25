from telegram import Update
from telegram.ext import CallbackContext
from rgbmatrix import graphics
from utils import authorized
import utils


def parse_text(string):
    utils.last_text_input = string

    text_lines = []
    current_line = 0

    font_dimensions = get_font_dimensions()

    if "|" not in string:  # pipe is newline character
        split = string.split(" ")

        # loop through all words
        # created a helper TextLine class to hold import line information and calculate placement at a later step
        for i in range(0, len(split)):
            if current_line >= len(text_lines):  # check if new line is greater than the length, append it to list if so for later reference
                text_lines.append(TextLine(line_number=current_line, line_text=split[i]))
            elif (len(text_lines[current_line].line_text) + len(split[i]) + 1) <= get_font_dimensions()[1]:  # if we can fit in more words, add them on
                text_lines[current_line].line_text = text_lines[current_line].line_text + " " + split[i]
            else:  # we are out of space, create a new line
                current_line += 1

                # calculate max displayable lines taking into account the font size
                # if we exceed the max displayable, kill the loop to conserve processing power
                max_lines = font_dimensions[2] if utils.show_text == 1 else font_dimensions[2] * 2
                if current_line > max_lines - 1:
                    break

                # append new line top
                text_lines.append(TextLine(line_number=current_line, line_text=split[i]))
    else:
        split = string.split("|")  # override the natural split using new line

        for i in range(0, len(split)):
            current_line_text = split[i][0:get_font_dimensions()[1]]    # split into the max characters considering font size

            max_lines = font_dimensions[2] if utils.show_text == 1 else font_dimensions[2] * 2
            if current_line > max_lines - 1:
                break

            # append custom line to the top of the lines list
            text_lines.append(TextLine(line_number=i, line_text=current_line_text))

    utils.text_lines = text_lines.copy()        # send a copy of the text lines list to the utils holder class


def text(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    string = update.message.text.replace("/text ", "")      # catch text for bottom half and full screen
    string = string.replace("/textf ", "")

    utils.show_text = 2 if "textf" in update.message.text else 1      # 3 part variable, 0 is no text, 1 is half, 2 is full
    utils.update_board = True

    parse_text(string)      # parse inputted text; separated into a new method so we can reparse text on font change


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
    if night:   # night colors for matrix
        utils.red_color = graphics.Color(160, 0, 0)
        utils.purple_color = graphics.Color(128, 0, 0)
        utils.blue_color = graphics.Color(128, 0, 0)
        utils.text_color = graphics.Color(128, 0, 0)
    else:       # day time colors for the matrix
        utils.red_color = graphics.Color(255, 0, 0)
        utils.purple_color = graphics.Color(156, 0, 156)
        utils.blue_color = graphics.Color(0, 64, 255)
        utils.text_color = graphics.Color(0, 64, 255)


# return the font size dimensions, followed by how many characters fit on a line, then how many lines on a half matrix
def get_font_dimensions():
    if utils.font_size == 0:
        return 5, 12, 4
    elif utils.font_size == 1:
        return 6, 10, 3
    else:
        return 8, 8, 2


# helper class to hold line information
class TextLine:
    line_number: int
    line_text: str

    def __init__(self, line_number, line_text):
        self.line_number = line_number
        self.line_text = line_text

    # use the positioning formulas to calculate how to center each line and where to put each y value
    def parse_position(self):
        font_dimensions = get_font_dimensions()

        x_value = int((64 - (font_dimensions[0] * len(self.line_text))) / 2)

        if utils.font_size == 0:
            y_value = (8 * (self.line_number % font_dimensions[2])) + 7
        elif utils.font_size == 1:
            y_value = (10 * (self.line_number % font_dimensions[2])) + 9
        else:
            y_value = (16 * (self.line_number % font_dimensions[2])) + 13

        # add 32 to the current y value for text in the bottom half of the screen
        if utils.show_text == 1 or (utils.show_text == 2 and self.line_number > font_dimensions[2] - 1):
            y_value += 32

        return x_value, y_value
