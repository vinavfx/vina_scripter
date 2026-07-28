from ..nuke_util.pyside import (
    QtGui,
    QRegExp,
)

import nuke  # type: ignore
from .blink_highlighter import onedark


class KSPythonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, style="monokai"):
        super(KSPythonHighlighter, self).__init__(None)

        self.selected_text = ""
        self.selected_text_prev = ""

        self.blocked = False

        self.styles = self.loadStyles()
        self._style = style
        self.setStyle(self._style)

    def loadStyles(self):
        styles = dict()

        default_styles_list = [
            {
                "title": "nuke",
                "styles": {
                    "base": self.format([255, 255, 255]),
                    "keyword": self.format([238, 117, 181], "bold"),
                    "operator": self.format([238, 117, 181], "bold"),
                    "number": self.format(onedark["orange"]),
                    "singleton": self.format([174, 129, 255]),
                    "string": self.format([242, 136, 135]),
                    "comment": self.format([143, 221, 144]),
                },
                "keywords": {},
            },
            {
                "title": "monokai",
                "styles": {
                    "base": self.format(onedark["white"]),
                    "keyword": self.format(onedark["purpure"]),
                    "operator": self.format(onedark["pink"]),
                    "string": self.format(onedark["green"]),
                    "comment": self.format(onedark["gray"]),
                    "number": self.format(onedark["orange"]),
                    "singleton": self.format(onedark["purpure"]),
                    "function": self.format(onedark["blue"]),
                    "argument": self.format(onedark["yellow"], "italic"),
                    "class": self.format(onedark["pink"]),
                    "callable": self.format(onedark["blue"]),
                    "error": self.format([130, 226, 255], "italic"),
                    "underline": self.format(onedark["cyan"], "underline"),
                    "selected": self.format(onedark["yellow"], "bold underline"),
                    "custom": self.format(onedark["white"], "italic"),
                    "blue": self.format(onedark["purpure"], "italic"),
                    "self": self.format(onedark["pink"], "italic"),
                    "fstring_expr": self.format([171, 178, 191]),
                },
                "keywords": {
                    "custom": ["nuke"],
                    "blue": [
                        "def",
                        "class",
                        "int",
                        "str",
                        "float",
                        "bool",
                        "list",
                        "dict",
                        "set",
                    ],
                    "base": [],
                    "self": ["self"],
                },
            },
        ]
        for style_dict in default_styles_list:
            if all(k in style_dict.keys() for k in ["title", "styles"]):
                styles[style_dict["title"]] = self.loadStyle(style_dict)

        return styles

    def loadStyle(self, style_dict):
        styles = style_dict["styles"].copy()

        if "base" in styles:
            base_format = styles["base"]
        else:
            base_format = self.format([255, 255, 255])

        main_keywords = [
            "and",
            "assert",
            "break",
            "continue",
            "del",
            "elif",
            "else",
            "except",
            "exec",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "not",
            "or",
            "pass",
            "print",
            "raise",
            "return",
            "try",
            "while",
            "yield",
            "with",
            "as",
        ]

        error_keywords = [
            "AssertionError",
            "AttributeError",
            "EOFError",
            "FloatingPointError",
            "FloatingPointError",
            "GeneratorExit",
            "ImportError",
            "IndexError",
            "KeyError",
            "KeyboardInterrupt",
            "MemoryError",
            "NameError",
            "NotImplementedError",
            "OSError",
            "OverflowError",
            "ReferenceError",
            "RuntimeError",
            "StopIteration",
            "SyntaxError",
            "IndentationError",
            "TabError",
            "SystemError",
            "SystemExit",
            "TypeError",
            "UnboundLocalError",
            "UnicodeError",
            "UnicodeEncodeError",
            "UnicodeDecodeError",
            "UnicodeTranslateError",
            "ValueError",
            "ZeroDivisionError",
        ]

        base_keywords = [","]

        operator_keywords = [
            "=",
            "==",
            "!=",
            "<",
            "<=",
            ">",
            ">=",
            "\+",
            "-",
            "\*",
            "/",
            "//",
            "\%",
            "\*\*",
            "\+=",
            "-=",
            "\*=",
            "/=",
            "\%=",
            "\^",
            "\|",
            "\&",
            "\~",
            ">>",
            "<<",
        ]

        singletons = ["True", "False", "None"]

        if "comment" in styles:
            tri_single = (QRegExp("'''"), 1, styles["string"])
            tri_double = (QRegExp('"""'), 2, styles["string"])
        else:
            tri_single = (QRegExp("'''"), 1, base_format)
            tri_double = (QRegExp('"""'), 2, base_format)

        rules = []

        if "argument" in styles:
            rules += [(r"def [\w]+[\s]*\((.*)\)", 1, styles["argument"])]
            rules += [(i, 0, base_format) for i in base_keywords]
            rules += [(r"[^\(\w),.][\s]*[\w]+", 0, base_format)]

        if "callable" in styles:
            rules += [(r"\b([\w]+)[\s]*[(]", 1, styles["callable"])]

        if "keyword" in styles:
            rules += [(r"\b%s\b" % i, 0, styles["keyword"]) for i in main_keywords]

        if "error" in styles:
            rules += [(r"\b%s\b" % i, 0, styles["error"]) for i in error_keywords]

        if "operator" in styles:
            rules += [(i, 0, styles["operator"]) for i in operator_keywords]

        if "singleton" in styles:
            rules += [(r"\b%s\b" % i, 0, styles["singleton"]) for i in singletons]

        if "number" in styles:
            rules += [(r"\b[0-9]+\b", 0, styles["number"])]

        if "function" in styles:
            rules += [(r"def[\s]+([\w\.]+)", 1, styles["function"])]
            rules += [(r"@([\w\.]+)", 1, styles["function"])]

        if "class" in styles:
            rules += [(r"class[\s]+([\w\.]+)", 1, styles["class"])]
            rules += [(r"class[\s]+[\w\.]+[\s]*\((.*)\)", 1, styles["class"])]

        if "argument" in styles:
            rules += [(r"def[\s]+[\w]+[\s]*\(([\w]+)", 1, styles["argument"])]

        if "keywords" in style_dict.keys():
            keywords = style_dict["keywords"]
            for k in keywords.keys():
                if k in styles:
                    rules += [(r"\b%s\b" % i, 0, styles[k]) for i in keywords[k]]

        if "string" in styles:
            rules += [(r'"[^"\\]*(\\.[^"\\]*)*"', 0, styles["string"])]
            rules += [(r"'[^'\\]*(\\.[^'\\]*)*'", 0, styles["string"])]

        if "comment" in styles:
            rules += [(r"#[^\n]*", 0, styles["comment"])]

        result = {
            "rules": [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules],
            "tri_single": tri_single,
            "tri_double": tri_double,
            "formats": styles,
        }

        return result

    @staticmethod
    def format(rgb, style=""):
        color = QtGui.QColor(*rgb)
        text_format = QtGui.QTextCharFormat()
        text_format.setForeground(color)

        if "bold" in style:
            text_format.setFontWeight(QtGui.QFont.Bold)
        if "italic" in style:
            text_format.setFontItalic(True)
        if "underline" in style:
            text_format.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)

        return text_format

    def highlightBlock(self, text):
        string_format = self.styles[self._style]["formats"].get("string")
        comment_format = self.styles[self._style]["formats"].get("comment")

        string_ranges = []

        for expression, nth, text_format in self.styles[self._style]["rules"]:
            is_string_rule = string_format is not None and text_format == string_format
            is_comment_rule = comment_format is not None and text_format == comment_format

            current_pos = 0
            index = expression.indexIn(text, current_pos)

            while index >= 0:
                match_index = expression.pos(nth)
                length = len(expression.cap(nth))
                total_match_len = expression.matchedLength()

                if total_match_len <= 0:
                    current_pos += 1
                    index = expression.indexIn(text, current_pos)
                    continue

                if length > 0 and match_index >= 0:
                    if is_comment_rule and any(start <= match_index < end for start, end in string_ranges):
                        current_pos = index + total_match_len
                        index = expression.indexIn(text, current_pos)
                        continue

                    try:
                        self.setFormat(match_index, length, text_format)
                    except:
                        return False

                    if is_string_rule:
                        string_ranges.append((match_index, match_index + length))

                current_pos = index + total_match_len
                index = expression.indexIn(text, current_pos)

        self.highlightFStringExpressions(text)

        self.setCurrentBlockState(0)

        in_multiline = self.match_multiline(text, *self.styles[self._style]["tri_single"], string_ranges=string_ranges)
        if not in_multiline:
            in_multiline = self.match_multiline(
                text, *self.styles[self._style]["tri_double"], string_ranges=string_ranges
            )

    def highlightFStringExpressions(self, text):
        formats = self.styles[self._style].get("formats", {})
        if "fstring_expr" not in formats:
            return

        fstring_pattern = QRegExp(r"""[fF]("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')""")
        brace_pattern = QRegExp(r"\{[^}]+\}")

        comment_index = QRegExp("#").indexIn(text)

        start = fstring_pattern.indexIn(text, 0)
        while start >= 0:
            match_len = fstring_pattern.matchedLength()
            if match_len <= 0:
                start = fstring_pattern.indexIn(text, start + 1)
                continue

            if comment_index >= 0 and start >= comment_index:
                break

            segment = text[start : start + match_len]

            b_index = brace_pattern.indexIn(segment, 0)
            while b_index >= 0:
                b_len = brace_pattern.matchedLength()
                if b_len <= 0:
                    break
                self.setFormat(start + b_index, b_len, formats["fstring_expr"])
                b_index = brace_pattern.indexIn(segment, b_index + b_len)

            start = fstring_pattern.indexIn(text, start + match_len)

    def setStyle(self, style_name="nuke"):
        if style_name in self.styles.keys():
            self._style = style_name
        else:
            raise Exception("Style {} not found.".format(str(style_name)))

    def match_multiline(self, text, delimiter, in_state, style, string_ranges=None):
        string_ranges = string_ranges or []

        def in_string(pos):
            return any(s <= pos < e for s, e in string_ranges)

        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:
            start = delimiter.indexIn(text)
            while start >= 0 and in_string(start):
                start = delimiter.indexIn(text, start + 1)
            add = delimiter.matchedLength() if start >= 0 else 0

        while start >= 0:
            end = delimiter.indexIn(text, start + add)
            while end >= 0 and in_string(end):
                end = delimiter.indexIn(text, end + 1)

            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            self.setFormat(start, length, style)

            start = delimiter.indexIn(text, start + length)
            while start >= 0 and in_string(start):
                start = delimiter.indexIn(text, start + 1)
            add = delimiter.matchedLength() if start >= 0 else 0

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
