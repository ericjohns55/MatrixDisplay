from telegram import Update
from telegram.ext import CallbackContext
from rgbmatrix import graphics
from drawing import *
import utils


def draw_circle_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = update.message.text
    split = text.split(" ")

    if len(split) == 5 or len(split) == 7:
        try:
            x = int(split[1])
            y = int(split[2])
            r = int(split[3])

            if len(split) == 5:
                color = utils.parse_color(split[4])
            else:
                color = graphics.Color(int(split[4]), int(split[5]), int(split[6]))

            utils.drawings.append(CircleDrawing(text, x, y, r, color))

            utils.update_board = True
        except ValueError:
            update.message.reply_text("Invalid arguments.\nUse /drawcircle [x] [y] [r] {[color] | [red] [green] [blue]}")
    else:
        update.message.reply_text("Invalid arguments.\nUse /drawcircle [x] [y] [r] {[color] | [red] [green] [blue]}")


def draw_rectangle_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = update.message.text
    split = text.split(" ")

    if len(split) == 7 or len(split) == 9:
        try:
            cx1 = int(split[1])
            cy1 = int(split[2])
            cx2 = int(split[3])
            cy2 = int(split[4])
            thickness = int(split[5])

            if len(split) == 7:
                color = utils.parse_color(split[6])
            else:
                color = graphics.Color(int(split[6]), int(split[7]), int(split[8]))

            utils.drawings.append(RectangleDrawing(text, cx1, cy1, cx2, cy2, thickness, color))

            utils.update_board = True
        except ValueError:
            update.message.reply_text("Invalid arguments.\nUse /drawrectangle [cx1] [cy1] [cx2] [cy2] [thickness] {[color] | [red] [green] [blue]}")
    else:
        update.message.reply_text("Invalid arguments.\nUse /drawrectangle [cx1] [cy1] [cx2] [cy2] [thickness] {[color] | [red] [green] [blue]}")


def draw_line_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = update.message.text
    split = text.split(" ")

    if len(split) == 6 or len(split) == 8:
        try:
            x1 = int(split[1])
            y1 = int(split[2])
            x2 = int(split[3])
            y2 = int(split[4])

            if len(split) == 6:
                color = utils.parse_color(split[5])
            else:
                color = graphics.Color(int(split[5]), int(split[6]), int(split[7]))

            utils.drawings.append(LineDrawing(text, x1, y1, x2, y2, color))

            utils.update_board = True
        except ValueError:
            update.message.reply_text("Invalid arguments.\nUse /drawline [x1] [y1] [x2] [y2] {[color] | [red] [green] [blue]}")
    else:
        update.message.reply_text("Invalid arguments.\nUse /drawline [x1] [y1] [x2] [y2] {[color] | [red] [green] [blue]}")


def draw_text_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    update.message.reply_text("NOT IMPLEMENTED YET")


def fill_area_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = update.message.text
    split = text.split(" ")

    if len(split) == 6 or len(split) == 8:
        try:
            x1 = int(split[1])
            y1 = int(split[2])
            x2 = int(split[3])
            y2 = int(split[4])

            if len(split) == 6:
                color = utils.parse_color(split[5])
            else:
                color = graphics.Color(int(split[5]), int(split[6]), int(split[7]))

            utils.drawings.append(AreaDrawing(text, x1, y1, x2, y2, color))

            utils.update_board = True
        except ValueError:
            update.message.reply_text("Invalid arguments.\nUse /fillarea [x1] [y1] [x2] [y2] {[color] | [red] [green] [blue]}")
    else:
        update.message.reply_text("Invalid arguments.\nUse /fillarea [x1] [y1] [x2] [y2] {[color] | [red] [green] [blue]}")


def fill_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = update.message.text
    split = text.split(" ")

    if len(split) == 2 or len(split) == 4:
        try:
            if len(split) == 2:
                color = utils.parse_color(split[1])
            else:
                color = graphics.Color(int(split[1]), int(split[2]), int(split[3]))

            utils.drawings.append(BackgroundDrawing(text, color))

            utils.update_board = True
        except ValueError:
            update.message.reply_text("Invalid arguments.\nUse /fill {[color] | [red] [green] [blue]}")
    else:
        update.message.reply_text("Invalid arguments.\nUse /fill {[color] | [red] [green] [blue]}")


def list_scripts(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    scripts_list = "Current scripts:\n"

    for i in range(len(utils.drawings)):
        scripts_list += utils.drawings[i].command + "\n"

    scripts_list += "Type /clearscripts to remove all scripts."

    update.message.reply_text(scripts_list)


def clear_scripts(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    utils.drawings = []

    utils.update_board = True
