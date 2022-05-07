# Eric Johns
# MatrixDisplay
# https://github.com/ericjohns55/MatrixDisplay/

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from rgbmatrix import graphics
from PIL import Image
from io import BytesIO
import base64
import matrix_main
import drawing
import json
import os

screen_update_required = False
contains_clock_drawing = False
drawings_list = []


# some predefined colors i made for ease
def parse_colors(text):
    parsed = text.replace("[red]", "(128,0,0)").replace("[orange]", "(253,88,0)").replace("[yellow]", "(255,228,0)") \
        .replace("[green]", "(0,160,0)").replace("[blue]", "(0,64,255)").replace("[purple]", "(128,0,128)") \
        .replace("[pink]", "(228,0,228)").replace("[white]", "(255,255,255)").replace("[gray]", "(128,128,128") \
        .replace("[black]", "(0,0,0)").replace("[brown]", "(101,67,33)").replace("[night]", "(32,0,0)")
    return parsed


def circle_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = parse_colors(update.message.text)    # first part of the command is to parse the colors
    formatted = text[1:len(text)]               # remove the / part of the command and split
    split = formatted.split(" ")

    try:
        color_components = split[4].split(",")  # for the circle commands the color breakdown is index 4 of the split
        red = int(color_components[0][1:len(color_components[0])])
        green = int(color_components[1])
        blue = int(color_components[2][0:len(color_components[2]) - 1])

        x = int(split[1])       # grab the x, y, and radius values
        y = int(split[2])
        radius = int(split[3])

        circle = drawing.CircleDrawing(x, y, radius, graphics.Color(red, green, blue))  # create our drawing object

        global drawings_list
        drawings_list.append(circle)    # append it to the list

        global screen_update_required   # force screen update
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /circle\nCorrect usage: {0}".format(drawing.Drawing.get_args(drawing.DrawingType.CIRCLE)))


# ALL OTHER DRAWING COMMANDS FOLLOW A SIMILAR PATTERN


def rectangle_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = parse_colors(update.message.text)
    formatted = text[1:len(text)]
    split = formatted.split(" ")

    try:
        color_components = split[6].split(",")
        red = int(color_components[0][1:len(color_components[0])])
        green = int(color_components[1])
        blue = int(color_components[2][0:len(color_components[2]) - 1])

        x1 = int(split[1])
        y1 = int(split[2])
        x2 = int(split[3])
        y2 = int(split[4])
        thickness = int(split[5])

        rectangle = drawing.RectangleDrawing(x1, y1, x2, y2, thickness, graphics.Color(red, green, blue))

        global drawings_list
        drawings_list.append(rectangle)

        global screen_update_required
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /rectangle\nCorrect usage: {0}".format(drawing.Drawing.get_args(drawing.DrawingType.RECTANGLE)))


def line_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = parse_colors(update.message.text)
    formatted = text[1:len(text)]
    split = formatted.split(" ")

    try:
        color_components = split[5].split(",")
        red = int(color_components[0][1:len(color_components[0])])
        green = int(color_components[1])
        blue = int(color_components[2][0:len(color_components[2]) - 1])

        x1 = int(split[1])
        y1 = int(split[2])
        x2 = int(split[3])
        y2 = int(split[4])

        line = drawing.LineDrawing(x1, y1, x2, y2, graphics.Color(red, green, blue))

        global drawings_list
        drawings_list.append(line)

        global screen_update_required
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /line\nCorrect usage: {0}".format(drawing.Drawing.get_args(drawing.DrawingType.LINE)))


def fill_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = parse_colors(update.message.text)
    formatted = text[1:len(text)]
    split = formatted.split(" ")

    try:
        color_components = split[5].split(",")
        red = int(color_components[0][1:len(color_components[0])])
        green = int(color_components[1])
        blue = int(color_components[2][0:len(color_components[2]) - 1])

        x1 = int(split[1])
        y1 = int(split[2])
        x2 = int(split[3])
        y2 = int(split[4])

        fill = drawing.FillDrawing(x1, y1, x2, y2, graphics.Color(red, green, blue))

        global drawings_list
        drawings_list.append(fill)

        global screen_update_required
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /fill\nCorrect usage: {0}".format(drawing.Drawing.get_args(drawing.DrawingType.FILL)))


def background_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = parse_colors(update.message.text)
    formatted = text[1:len(text)]
    split = formatted.split(" ")

    try:
        color_components = split[1].split(",")
        red = int(color_components[0][1:len(color_components[0])])
        green = int(color_components[1])
        blue = int(color_components[2][0:len(color_components[2]) - 1])

        background = drawing.BackgroundDrawing(graphics.Color(red, green, blue))

        global drawings_list
        drawings_list.append(background)

        global screen_update_required
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /background\nCorrect usage: {0}".format(drawing.Drawing.get_args(drawing.DrawingType.BACKGROUND)))


def text_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = parse_colors(update.message.text)
    formatted = text[1:len(text)]
    split = formatted.split(" ")

    try:
        color_components = split[4].split(",")
        red = int(color_components[0][1:len(color_components[0])])
        green = int(color_components[1])
        blue = int(color_components[2][0:len(color_components[2]) - 1])

        x = int(split[1])
        y = int(split[2])
        font = split[3]
        message = text[(text.index(split[4]) + len(split[4]) + 1):len(text)]

        if x == -1:
            x = drawing.get_center_x(matrix_main.MATRIX_WIDTH, font, message)

        # offset the y value by the height of the font
        # this is because the default matrix library takes in an y value meaning the bottom of the text
        # i think thats a little unintuitive, so in my version the y position means the top of the word
        text_blob = drawing.TextDrawing(x, y + drawing.get_font_y(font), font, graphics.Color(red, green, blue), message)

        global drawings_list
        drawings_list.append(text_blob)

        global screen_update_required
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /text\nCorrect usage: {0}".format(drawing.Drawing.get_args(drawing.DrawingType.TEXT)))


def top_text_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = parse_colors(update.message.text)
    formatted = text[1:len(text)]
    split = formatted.split(" ")

    try:
        color_components = split[2].split(",")
        red = int(color_components[0][1:len(color_components[0])])
        green = int(color_components[1])
        blue = int(color_components[2][0:len(color_components[2]) - 1])

        font = split[1]
        message = text[(text.index(split[2]) + len(split[2]) + 1):len(text)]

        # default center top text and set the height to be the top of the matrix
        text_blob = drawing.TextDrawing(drawing.get_center_x(matrix_main.MATRIX_WIDTH, font, message),
                                        drawing.get_font_y(font), font, graphics.Color(red, green, blue), message)

        global drawings_list
        drawings_list.append(text_blob)

        global screen_update_required
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /toptext\nCorrect usage: {0}".format(drawing.Drawing.get_args(drawing.DrawingType.TOP_TEXT)))


def bottom_text_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = parse_colors(update.message.text)
    formatted = text[1:len(text)]
    split = formatted.split(" ")

    try:
        color_components = split[2].split(",")
        red = int(color_components[0][1:len(color_components[0])])
        green = int(color_components[1])
        blue = int(color_components[2][0:len(color_components[2]) - 1])

        font = split[1]
        message = text[(text.index(split[2]) + len(split[2]) + 1):len(text)]

        # default center bottom text and set the height to be the bottom of the matrix
        text_blob = drawing.TextDrawing(drawing.get_center_x(matrix_main.MATRIX_WIDTH, font, message),
                                        matrix_main.MATRIX_HEIGHT, font,
                                        graphics.Color(red, green, blue), message)

        global drawings_list
        drawings_list.append(text_blob)

        global screen_update_required
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /bottomtext\nCorrect usage: {0}".format(drawing.Drawing.get_args(drawing.DrawingType.BOTTOM_TEXT)))


def text_format_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = parse_colors(update.message.text)
    formatted = text[1:len(text)]
    split = formatted.split(" ")

    try:
        color_components = split[2].split(",")
        red = int(color_components[0][1:len(color_components[0])])
        green = int(color_components[1])
        blue = int(color_components[2][0:len(color_components[2]) - 1])

        font = split[1]
        message = text[(text.index(split[2]) + len(split[2]) + 1):len(text)]

        font_height = drawing.get_font_y(font)
        y_index = font_height

        global drawings_list

        if "|" not in message:  # theres no pipe, so we are going to split everything into individual lines
            font_length = drawing.get_font_x(font)
            temp_text_line = ""

            message_split = message.split(" ")  # split the message into words

            for i in range(0, len(message_split)):
                if temp_text_line == "":
                    temp_text_line = message_split[i]   # if our temp line is empty, make it the current word

                # otherwise: check if we can fit the next word on the temp line, if we CAN then append it with a space
                elif (len(temp_text_line) + len(message_split[i]) + 1) * font_length <= matrix_main.MATRIX_WIDTH:
                    temp_text_line += " " + message_split[i]
                else:
                    # word cannot fit, lets create a drawing of the temp line and push it to the display
                    text_blob = drawing.TextDrawing(drawing.get_center_x(matrix_main.MATRIX_WIDTH, font, temp_text_line),
                                                    y_index, font,
                                                    graphics.Color(red, green, blue), temp_text_line)
                    drawings_list.append(text_blob)

                    y_index += font_height  # this saves the height for the next loop incase there is more lines

                    temp_text_line = message_split[i]

            text_blob = drawing.TextDrawing(drawing.get_center_x(matrix_main.MATRIX_WIDTH, font, temp_text_line),
                                            y_index, font,
                                            graphics.Color(red, green, blue), temp_text_line)
            drawings_list.append(text_blob)

        else:
            message_split = message.split("|")  # user wants to use pipes to manually separate new lines

            for i in range(0, len(message_split)):  # draw each line individually and center them
                text_blob = drawing.TextDrawing(drawing.get_center_x(matrix_main.MATRIX_WIDTH, font, message_split[i]),
                                                y_index, font,
                                                graphics.Color(red, green, blue), message_split[i])
                drawings_list.append(text_blob)

                y_index += font_height

        global screen_update_required   # force update regardless
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /textf\nCorrect usage: {0}".format(drawing.Drawing.get_args(drawing.DrawingType.TEXT_FORMAT)))


def clock_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    text = parse_colors(update.message.text)
    formatted = text[1:len(text)]
    split = formatted.split(" ")

    try:
        color_components = split[4].split(",")
        red = int(color_components[0][1:len(color_components[0])])
        green = int(color_components[1])
        blue = int(color_components[2][0:len(color_components[2]) - 1])

        x = int(split[1])
        y = int(split[2])
        font = split[3]

        background = drawing.ClockDrawing(x, y + drawing.get_font_y(font), font, graphics.Color(red, green, blue))

        global drawings_list
        drawings_list.append(background)

        global screen_update_required
        screen_update_required = True

        global contains_clock_drawing   # set this to true so we know we need to update every minute
        contains_clock_drawing = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /clock\nCorrect usage: {0}".format(drawing.Drawing.get_args(drawing.DrawingType.CLOCK)))


def clear_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    clear_drawings()


def drawings_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    list_drawings(update)


def remove_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    try:
        index = int(update.message.text.replace("/remove ", ""))

        global drawings_list
        del drawings_list[index]    # delete the drawing at the given index

        global screen_update_required
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /remove\nCorrect usage: /remove [index of /drawings]")


def swap_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    try:
        split = update.message.text.replace("/swap ", "").split(" ")
        index1 = int(split[0])
        index2 = int(split[1])

        global drawings_list

        temp = drawings_list[index1]                    # swap the drawings order in the list
        drawings_list[index1] = drawings_list[index2]
        drawings_list[index2] = temp

        global screen_update_required
        screen_update_required = True
    except (ValueError, IndexError):
        generate_dismiss_keyboard(update, "Invalid use of /swap\nCorrect usage: /swap [index 1 of /drawings] [index 2]")


def save_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    global drawings_list

    json_string = json.dumps([current_drawing.send_to_json() for current_drawing in drawings_list]) # dump the json into a string

    file_name = matrix_main.DRAWINGS_FOLDER + update.message.text.replace("/save ", "/") + ".json"  # get the file name

    file = open(file_name, "w")     # write the json data to the file
    file.write(json_string)


def delete_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    file_name = matrix_main.DRAWINGS_FOLDER + update.message.text.replace("/delete ", "/") + ".json"

    if os.path.exists(file_name):   # delete the file if it exists
        os.remove(file_name)


def list_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    list_saved(update)


def load_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    global contains_clock_drawing
    contains_clock_drawing = False

    global drawings_list

    drawings_list.clear()

    try:
        file_name = matrix_main.DRAWINGS_FOLDER + update.message.text.replace("/load ", "/") + ".json"  # grab the font folder and file name

        with open(file_name, "r") as file:
            data = json.load(file)

            for i in range(len(data)):  # loop through each drawing found and create an object depending on the data type
                if int(data[i]["type"]) == drawing.DrawingType.CIRCLE.value[0]:
                    circle = drawing.CircleDrawing(int(data[i]["x"]), int(data[i]["y"]), int(data[i]["radius"]),
                                                   graphics.Color(int(data[i]["color"]["red"]), int(data[i]["color"]["green"]),
                                                                  int(data[i]["color"]["blue"])))
                    drawings_list.append(circle)
                elif int(data[i]["type"]) == drawing.DrawingType.RECTANGLE.value[0]:
                    rectangle = drawing.RectangleDrawing(int(data[i]["x1"]),
                                                         int(data[i]["y1"]),
                                                         int(data[i]["x2"]),
                                                         int(data[i]["y2"]),
                                                         int(data[i]["thickness"]),
                                                         graphics.Color(int(data[i]["color"]["red"]),
                                                                        int(data[i]["color"]["green"]),
                                                                        int(data[i]["color"]["blue"])))
                    drawings_list.append(rectangle)
                elif int(data[i]["type"]) == drawing.DrawingType.LINE.value[0]:
                    line = drawing.LineDrawing(int(data[i]["x1"]),
                                               int(data[i]["y1"]),
                                               int(data[i]["x2"]),
                                               int(data[i]["y2"]),
                                               graphics.Color(int(data[i]["color"]["red"]),
                                                              int(data[i]["color"]["green"]),
                                                              int(data[i]["color"]["blue"])))
                    drawings_list.append(line)
                elif int(data[i]["type"]) == drawing.DrawingType.FILL.value[0]:
                    fill = drawing.FillDrawing(int(data[i]["x1"]),
                                               int(data[i]["y1"]),
                                               int(data[i]["x2"]),
                                               int(data[i]["y2"]),
                                               graphics.Color(int(data[i]["color"]["red"]),
                                                              int(data[i]["color"]["green"]),
                                                              int(data[i]["color"]["blue"])))
                    drawings_list.append(fill)
                elif int(data[i]["type"]) == drawing.DrawingType.BACKGROUND.value[0]:
                    background = drawing.BackgroundDrawing(graphics.Color(int(data[i]["color"]["red"]),
                                                                          int(data[i]["color"]["green"]),
                                                                          int(data[i]["color"]["blue"])))
                    drawings_list.append(background)
                elif int(data[i]["type"]) == drawing.DrawingType.PICTURE.value[0]:
                    picture = drawing.PictureDrawing(Image.open(BytesIO(base64.b64decode(data[i]["image"]))))
                    drawings_list.append(picture)
                elif int(data[i]["type"]) == drawing.DrawingType.TEXT.value[0]:
                    text = drawing.TextDrawing(int(data[i]["x"]),
                                               int(data[i]["y"]),
                                               data[i]["font"],
                                               graphics.Color(int(data[i]["color"]["red"]),
                                                              int(data[i]["color"]["green"]),
                                                              int(data[i]["color"]["blue"])),
                                               data[i]["text"])
                    drawings_list.append(text)
                elif int(data[i]["type"]) == drawing.DrawingType.CLOCK.value[0]:
                    clock = drawing.ClockDrawing(int(data[i]["x"]),
                                                 int(data[i]["y"]),
                                                 data[i]["font"],
                                                 graphics.Color(int(data[i]["color"]["red"]),
                                                                int(data[i]["color"]["green"]),
                                                                int(data[i]["color"]["blue"])))
                    drawings_list.append(clock)

                    contains_clock_drawing = True

            global screen_update_required   # force update
            screen_update_required = True

            file.close()
    except (ValueError, IndexError, FileNotFoundError):
        generate_dismiss_keyboard(update, "Invalid JSON file provided.")


def buttons_command(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    usage_keyboard = [
        [
            InlineKeyboardButton(text="Circle", callback_data="usage_CIRCLE"),
            InlineKeyboardButton(text="Rectangle", callback_data="usage_RECTANGLE"),
            InlineKeyboardButton(text="Line", callback_data="usage_LINE")
        ],
        [
            InlineKeyboardButton(text="Fill", callback_data="usage_FILL"),
            InlineKeyboardButton(text="Background", callback_data="usage_BACKGROUND"),
            InlineKeyboardButton(text="Clock", callback_data="usage_CLOCK")
        ],
        [
            InlineKeyboardButton(text="Text", callback_data="usage_TEXT"),
            InlineKeyboardButton(text="Top Text", callback_data="usage_TOP_TEXT"),
            InlineKeyboardButton(text="Bottom Text", callback_data="usage_BOTTOM_TEXT")
        ],
        [
            InlineKeyboardButton(text="Text Format", callback_data="usage_TEXT_FORMAT"),
            InlineKeyboardButton(text="Picture Usage", callback_data="usage_PICTURE")
        ]
    ]

    data_persistence_keyboard = [
        [
            InlineKeyboardButton(text="Clear", callback_data="remove_drawings"),
            InlineKeyboardButton(text="Drawings", callback_data="list_drawings"),
            InlineKeyboardButton(text="Swap", callback_data="swap_usage"),
            InlineKeyboardButton(text="Remove", callback_data="remove_usage")
        ],
        [
            InlineKeyboardButton(text="List", callback_data="list_saved"),
            InlineKeyboardButton(text="Save", callback_data="save_usage"),
            InlineKeyboardButton(text="Load", callback_data="load_usage"),
            InlineKeyboardButton(text="Delete", callback_data="delete_usage")
        ]
    ]

    # create and send the inline keyboards
    update.message.reply_text("\U0000270F Command Usages \U0000270F", reply_markup=InlineKeyboardMarkup(usage_keyboard))
    update.message.reply_text("\U0001F5C2 Data Persistence Usages \U0001F5C2", reply_markup=InlineKeyboardMarkup(data_persistence_keyboard))


# callback data for the inline keyboard
def keyboard_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = str(query.data)

    if "dismiss" in data:
        query.delete_message()
    elif data.startswith("usage_"):
        drawing_type = data.replace("usage_", "")
        generate_dismiss_keyboard(update.callback_query, drawing.Drawing.get_args(drawing.DrawingType[drawing_type]))
    elif data == "swap_usage":
        generate_dismiss_keyboard(update.callback_query, "/swap [index 1 of /drawings] [index 2]")
    elif data == "remove_usage":
        generate_dismiss_keyboard(update.callback_query, "/remove [index of /drawings]")
    elif data == "save_usage":
        generate_dismiss_keyboard(update.callback_query, "/save [name of drawing]")
    elif data == "load_usage":
        generate_dismiss_keyboard(update.callback_query, "/load [name of drawing]")
    elif data == "delete_usage":
        generate_dismiss_keyboard(update.callback_query, "/delete [name of drawing]")
    elif data == "remove_drawings":
        clear_drawings()
    elif data == "list_drawings":
        list_drawings(update.callback_query)
    elif data == "list_saved":
        list_saved(update.callback_query)


def poll_image(update: Update, context: CallbackContext) -> None:
    update.message.delete()

    # get the most recent image sent and load it into a PIL Image object, resize it, then create our own drawing object from it
    file = context.bot.get_file(update.message.photo[-1].file_id)
    imported_image = Image.open(BytesIO(file.download_as_bytearray()))
    imported_image = imported_image.resize((matrix_main.MATRIX_WIDTH, matrix_main.MATRIX_HEIGHT), Image.ANTIALIAS)

    picture = drawing.PictureDrawing(imported_image)

    global drawings_list
    drawings_list.append(picture)

    global screen_update_required
    screen_update_required = True


def clear_drawings() -> None:
    global drawings_list
    drawings_list.clear()   # clear the list and force update

    global screen_update_required
    screen_update_required = True


def list_drawings(update: Update) -> None:
    global drawings_list

    message_text = "Current canvas drawings:\n"

    for i in range(len(drawings_list)):
        message_text += " " + str(i) + ": " + drawings_list[i].get_object_data() + "\n"

    generate_dismiss_keyboard(update, message_text)


def list_saved(update: Update) -> None:
    files = os.listdir(matrix_main.DRAWINGS_FOLDER)

    all_files = "Saved drawings:\n"

    for i in range(len(files)):
        all_files += " {0} - {1}\n".format((i + 1), files[i][0:files[i].find(".json")])

    generate_dismiss_keyboard(update, all_files)


# for quality of life of the user, add a dismiss button so they dont have to manually delete messages they dont need anymore
def generate_dismiss_keyboard(update: Update, message: str):
    keyboard = [[InlineKeyboardButton("Dismiss", callback_data='dismiss')]]
    update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
