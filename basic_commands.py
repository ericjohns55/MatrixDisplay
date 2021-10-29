from telegram import Update
from telegram.ext import CallbackContext
from rgbmatrix import graphics
from utils import authorized, ColorKeyboards
import utils
import sys
import os


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


def kill_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    utils.kill_program = True

    sys.exit(0)


def color_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    utils.update_board = True

    color = update.message.text

    if len(color.replace("/color ", "").split(" ")) == 3:     # custom rgb values, split at spaces in message
        rgb = color.replace("/color ", "").split(" ")
        utils.nonstandard_colors = True

        if utils.color_keyboard == ColorKeyboards.TEXT_COLOR:
            utils.text_color = graphics.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        elif utils.color_keyboard == ColorKeyboards.BACKGROUND_COLOR:
            utils.background_color = graphics.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        elif utils.color_keyboard == ColorKeyboards.DATE_COLOR:
            utils.date_color = graphics.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        elif utils.color_keyboard == ColorKeyboards.TIME_COLOR:
            utils.time_color = graphics.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        else:
            utils.weather_color = graphics.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    else:
        update.message.reply_text("Invalid arguments. Use /color [red] [green] [blue]")


def ping(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    update.message.reply_text("Bot is working correctly.")


def ip(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    if not authorized(update):
        return

    update.message.reply_text("Raspberry PI IP: " + utils.get_ip())
