from enum import Enum


class DrawingType(Enum):
    CIRCLE = 0,
    RECTANGLE = 1,
    LINE = 2,
    AREA = 3,
    BACKGROUND = 4,
    TEXT = 5


class Drawing:
    def __init__(self, drawing_type: DrawingType):
        self.type = drawing_type


class CircleDrawing(Drawing):
    def __init__(self, x: int, y: int, radius: int, color):
        super().__init__(DrawingType.CIRCLE)
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color


class RectangleDrawing(Drawing):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, thickness: int, color):
        super().__init__(DrawingType.RECTANGLE)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness
        self.color = color


class LineDrawing(Drawing):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color):
        super().__init__(DrawingType.RECTANGLE)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color


class AreaDrawing(Drawing):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color):
        super().__init__(DrawingType.RECTANGLE)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color


class BackgroundDrawing(Drawing):
    def __init__(self, color):
        super().__init__(DrawingType.BACKGROUND)
        self.color = color


class TextDrawing(Drawing):
    def __init__(self, x: int, y: int, font, color, text):
        super().__init__(DrawingType.TEXT)
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.text = text
