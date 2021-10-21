from telegram import Update
from dotenv import dotenv_values
from io import BytesIO
from PIL import Image
from rgbmatrix import graphics
import socket

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

forecast = "n/a"
temp = 0
real_feel = 0
wind = "0.0 mph"

update_board = True
text_lines = []
show_text = 0
show_image = False
image = None


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


def parse_image(file):
    imported = Image.open(BytesIO(file.download_as_bytearray()))  # convert to byte array to prevent saving locally
    imported = imported.resize((64, 64), Image.ANTIALIAS)  # resize to 64x64 for the 64x64 matrix

    image = Image.new(mode='RGB', size=(128, 32))
    # matrix unfortunately does not read in square, create long image so it reads as a line

    region1 = imported.crop((0, 0, 64, 32))  # copy top half into the left half of long image
    region2 = imported.crop((0, 32, 64, 64))  # copy bottom half into the right half of long image

    image.paste(region1, (0, 0, 64, 32))  # paste segments
    image.paste(region2, (64, 0, 128, 32))

    return image
