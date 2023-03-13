# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
from PySide2 import QtGui, QtCore

from .blink_highlighter import onedark


class tcl_highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self):
        super().__init__(None)
        self.styles = self.load_style()

    def load_style(self):
        green = self.format(onedark['green'])
        gray = self.format(onedark['gray'])
        pink = self.format(onedark['pink'])
        orange = self.format(onedark['orange'])
        purpure = self.format(onedark['purpure'])
        blue = self.format(onedark['blue'])
        cyan = self.format(onedark['cyan'])
        yellow = self.format(onedark['yellow'], 'italic')

        singletons = ['true', 'false', 'True', 'False']

        tri_single = (QtCore.QRegExp("'''"), 1, green)
        tri_double = (QtCore.QRegExp('"""'), 2, green)

        main_keywords = [
            "proc", "if", "while", "for", "foreach", "switch", "string",
            "list", "array", "catch", "return", "puts", "source", "incr", "rename",
            "continue", "unset", "append", "lindex", "incr", "concat", "regexp", "join",
            "format", "open", "close", "info", "eof", "seek", "else"
        ]

        keywords = [
            'set', 'expr', 'puts', 'exists', 'x', 'abs', 'acos', 'asin', 'atan', 'atan2',
            'ceil', 'clamp', 'cos', 'cosh', 'degrees', 'exp', 'exponent', 'fBm',
            'fabs', 'floor', 'fmod', 'frame', 'hypot', 'int', 'ldexp', 'lerp',
            'log', 'log10', 'logb', 'mantissa', 'max', 'min', 'mix', 'noise', 'pi',
            'pow', 'pow2', 'radians', 'random', 'rint', 'sin', 'sinh', 'smoothstep',
            'sqrt', 'step', 'tan', 'tanh', 'trunc', 'turbulence', 'y', 'exists'
        ]

        rules = []

        # Numbers
        rules += [(r'\b[0-9]+\b', 0, orange)]
        rules += [(i, 0, orange) for i in singletons]

        # Functions
        rules += [(r'proc\s+([\w\.]+)', 0, blue)]

        # KeyWords
        rules += [(r'\b%s\b' % i, 0, purpure) for i in main_keywords]
        rules += [(r'\b%s\b' % i, 0, yellow) for i in keywords]

        # Strings
        rules += [(r'"[^"\\]*(\\.[^"\\]*)*"', 0, green)]
        rules += [(r"'[^'\\]*(\\.[^'\\]*)*'", 0, green)]

        # Objects
        rules += [(r'\w+(?=\.)', 0, cyan)]
        rules += [(r'\b\d+\.\d+\b', 0, orange)] # omit float numbers

        # Variables
        rules += [(r'\$\w+', 0, pink)]
        rules += [(r'\$::\w+', 0, pink)]

        # Comments
        rules += [(r'#[^\n]*', 0, gray)]

        result = {
            "rules": [(QtCore.QRegExp(pat), index, fmt) for (pat, index, fmt) in rules],
            "tri_single": tri_single,
            "tri_double": tri_double,
        }

        return result

    def format(self, rgb, style=''):
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
        for expression, nth, text_format in self.styles["rules"]:
            index = expression.indexIn(text, 0)

            while index >= 0:
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                try:
                    self.setFormat(index, length, text_format)
                except:
                    return False
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
