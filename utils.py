from telegram import Update
from io import BytesIO
from PIL import Image
from rgbmatrix import graphics
from enum import Enum
import socket
import os


class ColorKeyboards(Enum):
    TEXT_COLOR = 0,
    BACKGROUND_COLOR = 1,
    DATE_COLOR = 2,
    TIME_COLOR = 3,
    WEATHER_COLOR = 4


# declare field variables
kill_program = False

time_color = graphics.Color(255, 0, 0)
date_color = graphics.Color(128, 0, 128)
weather_color = graphics.Color(0, 64, 255)
background_color = graphics.Color(0, 0, 0)
text_color = graphics.Color(0, 64, 255)

color_keyboard = ColorKeyboards.TEXT_COLOR

override_red = False
override_color = False
override_on = False
override_off = False

nonstandard_colors = False

forecast = "n/a"
temp = 0
real_feel = 0
wind = "0.0 mph"

canvas_mode = False
update_board = True
text_lines = []
show_text = 0
show_image = 0              # 3 part variable, 0 is no image, 1 is background, 2 is full image
image = None

font_size = 1
last_text_input = ""


# REFERENCED: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_ip():
    return [l for l in (
        [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
            [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
             [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]


# check authorized user, pretty much make sure its my user name because i do not want anyone else using the bot
def authorized(update: Update) -> bool:
    if update.message.from_user.username != os.environ["AUTHORIZED_USER"]:
        print("!!! LOG-IN ATTEMPT !!!\nUsername: " + update.message.from_user.username)
        update.message.reply_text("You are not authorized to use this bot.")
        return False
    return True


def parse_color(color):
    new_color = graphics.Color(0, 0, 0)

    if "red" in color:  # hard coded colors that can be used as a shortcut
        new_color = graphics.Color(128, 0, 0)
    if "orange" in color:
        new_color = graphics.Color(253, 88, 0)
    elif "yellow" in color:
        new_color = graphics.Color(255, 228, 0)
    elif "green" in color:
        new_color = graphics.Color(0, 160, 0)
    elif "blue" in color:
        new_color = graphics.Color(0, 64, 255)
    elif "purple" in color:
        new_color = graphics.Color(128, 0, 128)
    elif "pink" in color:
        new_color = graphics.Color(228, 0, 228)
    elif "brown" in color:
        new_color = graphics.Color(101, 67, 33)
    elif "white" in color:
        new_color = graphics.Color(255, 255, 255)
    elif "gray" in color:
        new_color = graphics.Color(128, 128, 128)
    elif "black" in color:
        new_color = graphics.Color(0, 0, 0)

    return new_color


def parse_image(file):
    imported = Image.open(BytesIO(file.download_as_bytearray()))  # convert to byte array to prevent saving locally
    imported = imported.resize((64, 64), Image.ANTIALIAS)  # resize to 64x64 for the 64x64 matrix

    """
    THE FOLLOWING CODE IS FOR TWO 64x32 MATRICES
    
    image = Image.new(mode='RGB', size=(128, 32))
    # matrix unfortunately does not read in square, create long image so it reads as a line

    region1 = imported.crop((0, 0, 64, 32))  # copy top half into the left half of long image
    region2 = imported.crop((0, 32, 64, 64))  # copy bottom half into the right half of long image

    image.paste(region1, (0, 0, 64, 32))  # paste segments
    image.paste(region2, (64, 0, 128, 32))
    
    RETURN IMAGE INSTEAD OF USING TWO 64x32 MATRICES
    """
    return imported
