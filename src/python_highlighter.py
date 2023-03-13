# Original version by Wouter Gilsing and modified by Adrian Pueyo.
# current version modified by Francisco Contreras
from PySide2 import QtWidgets, QtGui, QtCore

import nuke
from .blink_highlighter import onedark


class KSPythonHighlighter(QtGui.QSyntaxHighlighter):
    """
    Adapted from an original version by Wouter Gilsing. His comments:
    Modified, simplified version of some code found I found when researching:
    wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
    They did an awesome job, so credits to them. I only needed to make some
    modifications to make it fit my needs for KS.
    """

    def __init__(self, style="monokai"):
        super().__init__(None)

        self.selected_text = ""
        self.selected_text_prev = ""

        self.blocked = False

        self.styles = self.loadStyles()  # Holds a dict for each style
        self._style = style  # Can be set via setStyle
        self.setStyle(self._style)  # Set default style


    def loadStyles(self):
        """ Loads the different sets of rules """
        styles = dict()

        # LOAD ANY STYLE
        default_styles_list = [
            {
                "title": "nuke",
                "styles": {
                    'base': self.format([255, 255, 255]),
                    'keyword': self.format([238, 117, 181], 'bold'),
                    'operator': self.format([238, 117, 181], 'bold'),
                    'number': self.format(onedark['orange']),
                    'singleton': self.format([174, 129, 255]),
                    'string': self.format([242, 136, 135]),
                    'comment': self.format([143, 221, 144]),
                },
                "keywords": {},
            },
            {
                "title": "monokai",
                "styles": {
                    'base': self.format(onedark['white']),
                    'keyword': self.format(onedark['purpure']),
                    'operator': self.format(onedark['pink']),
                    'string': self.format(onedark['green']),
                    'comment': self.format(onedark['gray']),
                    'number': self.format(onedark['orange']),
                    'singleton': self.format(onedark['purpure']),
                    'function': self.format(onedark['blue']),
                    'argument': self.format(onedark['yellow'], 'italic'),
                    'class': self.format(onedark['pink']),
                    'callable': self.format(onedark['blue']),
                    'error': self.format([130, 226, 255], 'italic'),
                    'underline': self.format(onedark['cyan'], 'underline'),
                    'selected': self.format(onedark['yellow'], 'bold underline'),
                    'custom': self.format(onedark['white'], 'italic'),
                    'blue': self.format(onedark['purpure'], 'italic'),
                    'self': self.format(onedark['pink'], 'italic'),
                },
                "keywords": {
                    'custom': ['nuke'],
                    'blue': ['def', 'class', 'int', 'str', 'float',
                             'bool', 'list', 'dict', 'set', ],
                    'base': [],
                    'self': ['self'],
                },
            }
        ]
        # TODO separate the format before the loadstyle thing. should be done here before looping.
        for style_dict in default_styles_list:
            if all(k in style_dict.keys() for k in ["title", "styles"]):
                styles[style_dict["title"]] = self.loadStyle(style_dict)

        return styles

    def loadStyle(self, style_dict):
        """
        Given a dictionary of styles and keywords, returns the style as a dict
        """

        styles = style_dict["styles"].copy()

        # 1. Base settings
        if "base" in styles:
            base_format = styles["base"]
        else:
            base_format = self.format([255, 255, 255])

        main_keywords = [
            'and', 'assert', 'break', 'continue',
            'del', 'elif', 'else', 'except', 'exec', 'finally',
            'for', 'from', 'global', 'if', 'import', 'in',
            'is', 'lambda', 'not', 'or', 'pass', 'print',
            'raise', 'return', 'try', 'while', 'yield', 'with', 'as'
        ]

        error_keywords = ['AssertionError', 'AttributeError', 'EOFError', 'FloatingPointError',
                          'FloatingPointError', 'GeneratorExit', 'ImportError', 'IndexError',
                          'KeyError', 'KeyboardInterrupt', 'MemoryError', 'NameError',
                          'NotImplementedError', 'OSError', 'OverflowError', 'ReferenceError',
                          'RuntimeError', 'StopIteration', 'SyntaxError', 'IndentationError',
                          'TabError', 'SystemError', 'SystemExit', 'TypeError', 'UnboundLocalError',
                          'UnicodeError', 'UnicodeEncodeError', 'UnicodeDecodeError', 'UnicodeTranslateError',
                          'ValueError', 'ZeroDivisionError',
                          ]

        base_keywords = [',']

        operator_keywords = [
            '=', '==', '!=', '<', '<=', '>', '>=',
            '\+', '-', '\*', '/', '//', '\%', '\*\*',
            '\+=', '-=', '\*=', '/=', '\%=',
            '\^', '\|', '\&', '\~', '>>', '<<'
        ]

        singletons = ['True', 'False', 'None']

        if 'comment' in styles:
            tri_single = (QtCore.QRegExp("'''"), 1, styles['string'])
            tri_double = (QtCore.QRegExp('"""'), 2, styles['string'])
        else:
            tri_single = (QtCore.QRegExp("'''"), 1, base_format)
            tri_double = (QtCore.QRegExp('"""'), 2, base_format)

        # 2. Rules
        rules = []

        if "argument" in styles:
            # Everything inside parentheses
            rules += [(r"def [\w]+[\s]*\((.*)\)", 1, styles['argument'])]
            # Now restore unwanted stuff...
            rules += [(i, 0, base_format) for i in base_keywords]
            rules += [(r"[^\(\w),.][\s]*[\w]+", 0, base_format)]

        if "callable" in styles:
            rules += [(r"\b([\w]+)[\s]*[(]", 1, styles['callable'])]

        if "keyword" in styles:
            rules += [(r'\b%s\b' % i, 0, styles['keyword'])
                      for i in main_keywords]

        if "error" in styles:
            rules += [(r'\b%s\b' % i, 0, styles['error'])
                      for i in error_keywords]

        if "operator" in styles:
            rules += [(i, 0, styles['operator']) for i in operator_keywords]

        if "singleton" in styles:
            rules += [(r'\b%s\b' % i, 0, styles['singleton'])
                      for i in singletons]

        if "number" in styles:
            rules += [(r'\b[0-9]+\b', 0, styles['number'])]

        # Function definitions
        if "function" in styles:
            rules += [(r"def[\s]+([\w\.]+)", 1, styles['function'])]

        # Class definitions
        if "class" in styles:
            rules += [(r"class[\s]+([\w\.]+)", 1, styles['class'])]
            # Class argument (which is also a class so must be same color)
            rules += [(r"class[\s]+[\w\.]+[\s]*\((.*)\)", 1, styles['class'])]

        # Function arguments
        if "argument" in styles:
            rules += [(r"def[\s]+[\w]+[\s]*\(([\w]+)", 1, styles['argument'])]

        # Custom keywords
        if "keywords" in style_dict.keys():
            keywords = style_dict["keywords"]
            for k in keywords.keys():
                if k in styles:
                    rules += [(r'\b%s\b' % i, 0, styles[k])
                              for i in keywords[k]]

        if "string" in styles:
            # Double-quoted string, possibly containing escape sequences
            rules += [(r'"[^"\\]*(\\.[^"\\]*)*"', 0, styles['string'])]
            # Single-quoted string, possibly containing escape sequences
            rules += [(r"'[^'\\]*(\\.[^'\\]*)*'", 0, styles['string'])]

        # Comments from '#' until a newline
        if "comment" in styles:
            rules += [(r'#[^\n]*', 0, styles['comment'])]

        # 3. Resulting dictionary
        result = {
            "rules": [(QtCore.QRegExp(pat), index, fmt) for (pat, index, fmt) in rules],
            # Build a QRegExp for each pattern
            "tri_single": tri_single,
            "tri_double": tri_double,
        }

        return result

    @staticmethod
    def format(rgb, style=''):
        """
        Return a QtWidgets.QTextCharFormat with the given attributes.
        """

        color = QtGui.QColor(*rgb)
        text_format = QtGui.QTextCharFormat()
        text_format.setForeground(color)

        if 'bold' in style:
            text_format.setFontWeight(QtGui.QFont.Bold)
        if 'italic' in style:
            text_format.setFontItalic(True)
        if 'underline' in style:
            text_format.setUnderlineStyle(
                QtGui.QTextCharFormat.SingleUnderline)

        return text_format

    def highlightBlock(self, text):
        """
        Apply syntax highlighting to the given block of text.
        """

        for expression, nth, text_format in self.styles[self._style]["rules"]:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                try:
                    self.setFormat(index, length, text_format)
                except:
                    return False
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Multi-line strings etc. based on selected scheme
        in_multiline = self.match_multiline(
            text, *self.styles[self._style]["tri_single"])
        if not in_multiline:
            in_multiline = self.match_multiline(
                text, *self.styles[self._style]["tri_double"])

        # TODO if there's a selection, highlight same occurrences in the full document.
        #   If no selection but something highlighted, unhighlight full document. (do it thru regex or sth)

    def setStyle(self, style_name="nuke"):
        if style_name in self.styles.keys():
            self._style = style_name
        else:
            raise Exception("Style {} not found.".format(str(style_name)))

    def match_multiline(self, text, delimiter, in_state, style):
        """
        Check whether highlighting requires multiple lines.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style_name="nuke"):
        self.setStyle(style_name)
