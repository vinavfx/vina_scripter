# Original version by Adrian Pueyo.
# current version modified by Francisco Contreras
from PySide2 import QtGui, QtCore
import re

onedark = {
    'dark': [40, 44, 52],  # 282c34
    'pink': [224, 108, 117],  # e06c75
    'green': [152, 195, 121],  # 98c379
    'yellow': [229, 192, 123],  # e5c07b
    'orange': [212, 145, 91],  # d4915b
    'blue': [97, 175, 239],  # 61afef
    'purpure': [198, 120, 221],  # c678dd
    'cyan': [86, 182, 194],  # 56b6c2
    'white': [200, 200, 200],
    'gray': [120, 120, 120],
}


class KSBlinkHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self,  style="default"):
        super().__init__(None)
        self.styles = self.loadStyles()
        self._style = style
        self._style = "default"


    def loadStyles(self):
        styles = dict()

        default_styles_list = [
            {
                "title": "default",
                "desc": "My adaptation from the default style from Nuke, with some improvements.",
                "styles": {
                    'keyword': (onedark['pink'], 'italic'),
                    'stringDoubleQuote': (onedark['green']),
                    'stringSingleQuote': (onedark['green']),
                    'comment': (onedark['gray']),
                    'multiline_comment': (onedark['gray']),
                    'type': (onedark['cyan']),
                    'variableKeyword': (onedark['yellow']),
                    'function': (onedark['blue']),
                    'number': (onedark['orange']),
                    'custom': (onedark['blue'], 'italic'),
                    'selected': ([255, 255, 255], 'bold underline'),
                    'underline': ([240, 240, 240], 'underline'),
                    'operator': (onedark['purpure'])
                },
                "keywords": {},
            },
        ]

        for style_dict in default_styles_list:
            if all(k in style_dict.keys() for k in ["title", "styles"]):
                styles[style_dict["title"]] = self.loadStyle(style_dict)

        return styles

    def loadStyle(self, style_dict):
        styles = style_dict["styles"]

        if "base" in styles:
            base_format = styles["base"]
        else:
            base_format = self.format([255, 255, 255])

        for key in styles:
            if type(styles[key]) == list:
                styles[key] = self.format(styles[key])
            elif styles[key][1]:
                styles[key] = self.format(styles[key][0], styles[key][1])

        mainKeywords = [
            "class", "const", "enum", "explicit",
            "friend", "inline", "long", "namespace", "operator",
            "private", "protected", "public", "short", "signed",
            "static", "struct", "template", "typedef", "typename",
            "union", "unsigned", "virtual", "volatile",
            "local", "param", "kernel", 'for', 'continue',
            'return', 'if', 'else', 'while', 'true', 'false'
        ]

        operatorKeywords = [
            '=', '==', '!=', '<', '<=', '>', '>=',    '\+', '-', '\*', '/', '//', '\%',
            '\*\*',    '\+=', '-=', '\*=', '/=', '\%=',    '\^', '\|', '\&', '\~', '>>', '<<', '\+\+',
            '&', '?', '+', '-', '*', '%', '!'
        ]

        variableKeywords = [
            "int", "int2", "int3", "int4",
            "float", "float2", "float3", "float4", "float3x3", "float4x4", "bool",
            "char", "double", "void"
        ]

        blinkTypes = [
            "Image", "eRead", "eWrite", "eReadWrite", "eEdgeClamped", "eEdgeConstant", "eEdgeNull",
            "eAccessPoint", "eAccessRanged1D", "eAccessRanged2D", "eAccessRandom",
            "eComponentWise", "ePixelWise", "ImageComputationKernel",
        ]

        blinkFunctions = [
            "define", "defineParam", "process", "init", "setRange", "setAxis", "median", "bilinear",
        ]

        if 'multiline_comments' in styles:
            multiline_delimiter = (QtCore.QRegExp(
                "/\\*"), QtCore.QRegExp("\\*/"), 1, styles['multiline_comments'])
        else:
            multiline_delimiter = (QtCore.QRegExp(
                "/\\*"), QtCore.QRegExp("\\*/"), 1, base_format)

        rules = []

        # Keywords
        if 'number' in styles:
            rules += [(r'\b\d+\b', 0, styles['number'])]

        # Floating-point literals
        if 'number' in styles:
            rules += [(r'\b\d+\.\d*(?:f)?\b', 0, styles['number'])]

        if 'keyword' in styles:
            rules += [(r'\b%s\b' % i, 0, styles['keyword'])
                      for i in mainKeywords]

        # Funcs
        if 'function' in styles:
            rules += [(r'\b\w+\s*(?=\()', 0, styles['function'])]
            rules += [(r'\b%s\b' % i, 0, styles['function'])
                      for i in blinkFunctions]

        # Types
        if 'type' in styles:
            rules += [(r'\b%s\b' % i, 0, styles['type']) for i in blinkTypes]

        if 'variableKeyword' in styles:
            rules += [(r'\b%s\b' % i, 0, styles['variableKeyword'])
                      for i in variableKeywords]

        #  Operators
        if 'operator' in styles:
            rules += [(r'%s' % re.escape(i), 0, styles['operator'])
                      for i in operatorKeywords]

        # String Literals
        if 'stringDoubleQuote' in styles:
            rules += [(r"\"([^\"\\\\]|\\\\.)*\"", 0,
                       styles['stringDoubleQuote'])]

        # String single quotes
        if 'stringSingleQuote' in styles:
            rules += [(r"'([^'\\\\]|\\\\.)*'", 0, styles['stringSingleQuote'])]

        # Comments
        if 'comment' in styles:
            rules += [(r"//[^\n]*", 0, styles['comment'])]

        # Return all rules
        result = {
            "rules": [(QtCore.QRegExp(pat), index, fmt) for (pat, index, fmt) in rules],
            "multiline_delimiter": multiline_delimiter,
        }
        return result

    def format(self, rgb, style=''):
        color = QtGui.QColor(*rgb)
        textFormat = QtGui.QTextCharFormat()
        textFormat.setForeground(color)

        if 'bold' in style:
            textFormat.setFontWeight(QtGui.QFont.Bold)
        if 'italic' in style:
            textFormat.setFontItalic(True)
        if 'underline' in style:
            textFormat.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)

        return textFormat

    def highlightBlock(self, text):
        for expression, nth, format in self.styles[self._style]["rules"]:
            index = expression.indexIn(text, 0)

            while index >= 0:
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        self.match_multiline_blink(
            text, *self.styles[self._style]["multiline_delimiter"])

    def match_multiline_blink(self, text, delimiter_start, delimiter_end, in_state, style):
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:
            start = delimiter_start.indexIn(text)
            add = delimiter_start.matchedLength()

        while start >= 0:
            end = delimiter_end.indexIn(text, start + add)
            if end >= add:
                length = end - start + add + delimiter_end.matchedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            self.setFormat(start, length, style)

            start = delimiter_start.indexIn(text, start + length)

        if self.currentBlockState() == in_state:
            return True
        else:
            return False
