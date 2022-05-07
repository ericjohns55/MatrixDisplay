# Eric Johns
# MatrixDisplay
# https://github.com/ericjohns55/MatrixDisplay/

from rgbmatrix import graphics
from PIL import Image
from enum import Enum
from io import BytesIO
import base64
import matrix_main


class DrawingType(Enum):
    CIRCLE = 0,
    RECTANGLE = 1,
    LINE = 2,
    FILL = 3,
    BACKGROUND = 4,
    PICTURE = 5,
    TEXT = 6,
    CLOCK = 7,
    TOP_TEXT = 8,
    BOTTOM_TEXT = 9,
    TEXT_FORMAT = 10


class Drawing:
    def __init__(self, drawing_type: DrawingType):
        self.type = drawing_type

    def get_type(self):
        return self.type

    @staticmethod
    def get_args(drawing_type: DrawingType):        # used in the usages inline keyboard to figure out how each command works
        if drawing_type == DrawingType.CIRCLE:
            return "/circle (x-pos) (y-pos) (radius) [color|(r,g,b)]"
        elif drawing_type == DrawingType.RECTANGLE:
            return "/rectangle (start-x) (start-y) (end-x) (end-y) (thickness) [color|(r,g,b)]"
        elif drawing_type == DrawingType.LINE:
            return "/line (start-x) (start-y) (end-x) (end-y) [color|(r,g,b)]"
        elif drawing_type == DrawingType.FILL:
            return "/fill (start-x) (start-y) (end-x) (end-y) [color|(r,g,b)]"
        elif drawing_type == DrawingType.BACKGROUND:
            return "/background [color|(r,g,b)]"
        elif drawing_type == DrawingType.PICTURE:
            return "Upload a picture into this chat and it will push to the display."
        elif drawing_type == DrawingType.TEXT:
            return "/text (x-pos) (y-pos) (font-size) [color|(r,g,b)] <text>"
        elif drawing_type == DrawingType.CLOCK:
            return "/clock (x-pos) (y-pos) (font-size) [color|(r,g,b)]"
        elif drawing_type == DrawingType.TOP_TEXT:
            return "/toptext (font) [color|(r,g,b)] <text>"
        elif drawing_type == DrawingType.BOTTOM_TEXT:
            return "/bottomtext (font) [color|(r,g,b)] <text>"
        elif drawing_type == DrawingType.TEXT_FORMAT:
            return "/textf (font) [color|(r,g,b)] <text>"
        else:
            return "Unknown"


class CircleDrawing(Drawing):
    def __init__(self, x: int, y: int, radius: int, color: graphics.Color):
        super().__init__(DrawingType.CIRCLE)
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def get_object_data(self):
        return "Circle - ({0}, {1}) - Radius: {2} - RGB: ({3},{4},{5})"\
            .format(self.x, self.y, self.radius, self.color.red, self.color.green, self.color.blue)

    def send_to_json(self):     # this is used when we export the drawing list to JSON - separates each drawing into smaller steps
        data = {"type": int(DrawingType.CIRCLE.value[0]), "x": self.x, "y": self.y, "radius": self.radius, "color": {"red": self.color.red, "green": self.color.green, "blue": self.color.blue}}
        return data


class RectangleDrawing(Drawing):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, thickness: int, color: graphics.Color):
        super().__init__(DrawingType.RECTANGLE)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness
        self.color = color

    def get_object_data(self):
        return "Rectangle - ({0}, {1} to {2}, {3}) - Thickness: {4} - RGB: ({5},{6},{7})"\
            .format(self.x1, self.y1, self.x2, self.y2, self.thickness, self.color.red, self.color.green, self.color.blue)

    def send_to_json(self):
        data = {"type": int(DrawingType.RECTANGLE.value[0]), "x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2, "thickness": self.thickness, "color": {"red": self.color.red, "green": self.color.green, "blue": self.color.blue}}
        return data


class LineDrawing(Drawing):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: graphics.Color):
        super().__init__(DrawingType.LINE)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color

    def get_object_data(self):
        return "Line - ({0}, {1} - {2}, {3}) - RGB: ({4},{5},{6})"\
            .format(self.x1, self.y1, self.x2, self.y2, self.color.red, self.color.green, self.color.blue)

    def send_to_json(self):
        data = {"type": int(DrawingType.LINE.value[0]), "x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2, "color": {"red": self.color.red, "green": self.color.green, "blue": self.color.blue}}
        return data


class FillDrawing(Drawing):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: graphics.Color):
        super().__init__(DrawingType.FILL)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color

    def get_object_data(self):
        return "Area Fill - ({0}, {1} - {2}, {3}) - RGB: ({4},{5},{6})"\
            .format(self.x1, self.y1, self.x2, self.y2, self.color.red, self.color.green, self.color.blue)

    def send_to_json(self):
        data = {"type": int(DrawingType.FILL.value[0]), "x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2, "color": {"red": self.color.red, "green": self.color.green, "blue": self.color.blue}}
        return data


class BackgroundDrawing(Drawing):
    def __init__(self, color: graphics.Color):
        super().__init__(DrawingType.BACKGROUND)
        self.color = color

    def get_object_data(self):
        return "Background Color - ({0},{1},{2})".format(self.color.red, self.color.green, self.color.blue)

    def send_to_json(self):
        data = {"type": int(DrawingType.BACKGROUND.value[0]), "color": {"red": self.color.red, "green": self.color.green, "blue": self.color.blue}}
        return data


class PictureDrawing(Drawing):
    def __init__(self, image: Image):
        super().__init__(DrawingType.PICTURE)
        self.image = image

    def get_object_data(self):
        return "Picture - Dimensions: ({0}, {1})".format(self.image.width, self.image.height)

    def send_to_json(self):
        buffered = BytesIO()        # when sending the image to JSON we convert into a base64 string
        self.image.save(buffered, format="JPEG")
        base64_string = base64.b64encode(buffered.getvalue())
        data = {"type": int(DrawingType.PICTURE.value[0]), "image": base64_string.decode("utf-8")}
        return data


class TextDrawing(Drawing):
    def __init__(self, x: int, y: int, font: str, color: graphics.Color, text: str):
        super().__init__(DrawingType.TEXT)
        self.font_folder = matrix_main.FONTS_FOLDER
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.text = text

    def get_object_data(self):
        return "Text - ({0}, {1}) - {2} - ({3},{4},{5}) - {6}"\
            .format(self.x, self.y, self.font, self.color.red, self.color.green, self.color.blue, self.text)

    def parse_font(self) -> graphics.Font:
        font = graphics.Font()
        font.LoadFont(self.font_folder + "/" + self.font + ".bdf")
        return font

    def send_to_json(self):
        data = {"type": int(DrawingType.TEXT.value[0]), "x": self.x, "y": self.y, "font": self.font, "color": {"red": self.color.red, "green": self.color.green, "blue": self.color.blue}, "text": self.text}
        return data


class ClockDrawing(Drawing):
    def __init__(self, x: int, y: int, font: str, color: graphics.Color):
        super().__init__(DrawingType.CLOCK)
        self.font_folder = matrix_main.FONTS_FOLDER
        self.x = x
        self.y = y
        self.font = font
        self.color = color

    def get_object_data(self):
        return "Clock - ({0}, {1}) - {2} - ({3},{4},{5})"\
            .format(self.x, self.y, self.font, self.color.red, self.color.green, self.color.blue)

    def parse_font(self) -> graphics.Font:
        font = graphics.Font()
        font.LoadFont(self.font_folder + "/" + self.font + ".bdf")
        return font

    def send_to_json(self):
        data = {"type": int(DrawingType.CLOCK.value[0]), "x": self.x, "y": self.y, "font": self.font, "color": {"red": self.color.red, "green": self.color.green, "blue": self.color.blue}}
        return data


def get_font_x(font):
    return int(font[0:font.index("x")])     # get the width of the font by finding the number before the 'x'


def get_font_y(font):
    format_offset = 0 if font[-1].isdigit() else 1  # if the last digit isnt a number (for bold it italic fonts), offset by 1
    font_height = int(font[(font.find("x") + 1):(len(font) - format_offset)])   # height of the font is everything past the x
    return font_height


def get_center_x(matrix_width, font, text):
    return (matrix_width - (len(text) * get_font_x(font))) / 2  # gets the center positioning for a given text in a font in the given matrix width

