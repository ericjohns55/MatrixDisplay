from rgbmatrix import graphics
from enum import Enum


class DrawingType(Enum):
    CIRCLE = 0,
    RECTANGLE = 1,
    LINE = 2,
    AREA = 3,
    BACKGROUND = 4,
    TEXT = 5


class Drawing:
    def __init__(self, drawing_type: DrawingType, command):
        self.type = drawing_type
        self.command = command


class CircleDrawing(Drawing):
    def __init__(self, command, x: int, y: int, radius: int, color: graphics.Color):
        super().__init__(DrawingType.CIRCLE, command)
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color


class RectangleDrawing(Drawing):
    def __init__(self, command, x1: int, y1: int, x2: int, y2: int, thickness: int, color: graphics.Color):
        super().__init__(DrawingType.RECTANGLE, command)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness
        self.color = color


class LineDrawing(Drawing):
    def __init__(self, command, x1: int, y1: int, x2: int, y2: int, color: graphics.Color):
        super().__init__(DrawingType.LINE, command)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color


class AreaDrawing(Drawing):
    def __init__(self, command, x1: int, y1: int, x2: int, y2: int, color: graphics.Color):
        super().__init__(DrawingType.AREA, command)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color


class BackgroundDrawing(Drawing):
    def __init__(self, command, color: graphics.Color):
        super().__init__(DrawingType.BACKGROUND, command)
        self.color = color


class TextDrawing(Drawing):
    def __init__(self, command, x: int, y: int, font, color, text: graphics.Color):
        super().__init__(DrawingType.TEXT, command)
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.text = text
