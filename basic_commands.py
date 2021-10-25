from telegram import Update
from telegram.ext import CallbackContext
from utils import authorized
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
