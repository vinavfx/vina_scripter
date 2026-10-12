# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
from ...nuke_util.pyside import QTextCursor


def enclose_word(_, cursor, param):
    char = chr(param["event"].key())

    left_char = char
    right_char = char

    if char in ["(", ")"]:
        left_char = "("
        right_char = ")"

    elif char in ["[", "]"]:
        left_char = "["
        right_char = "]"

    elif char in ["{", "}"]:
        left_char = "{"
        right_char = "}"

    pos = cursor.position()
    cursor.beginEditBlock()

    cursor.select(QTextCursor.WordUnderCursor)
    text = cursor.selectedText()

    cursor.removeSelectedText()

    new_text = "{}{}{}".format(left_char, text, right_char)
    cursor.insertText(new_text)
    cursor.setPosition(pos + 1)

    cursor.endEditBlock()

    return cursor


def surrounding_chars(char):
    if len(char) != 1:
        return None
    aliases = {"b": ")", "B": "}", "r": "]", "a": ">"}
    if char in aliases:
        char = aliases[char]
    for pair in ("()", "[]", "{}", "<>"):
        if char in pair:
            return pair
    if char in "\"'`":
        return char * 2
    return None


def find_surrounding(text, position, pair):
    left_char, right_char = pair
    stack = []
    quote = ""
    escaped = False
    quote_start = 0

    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                if quote == left_char and quote_start <= position <= index:
                    return quote_start, index
                quote = ""
            elif char == "\n":
                quote = ""
            continue
        if char in "\"'`" and (left_char != right_char or char == left_char):
            quote = char
            quote_start = index
        elif char == left_char:
            stack.append(index)
        elif char == right_char and stack:
            start = stack.pop()
            if start <= position <= index:
                return start, index
    return None


def remove_enclosed_word(_, cursor, param):
    return cursor


def replace_enclosed_word(self, cursor, param):
    source = self.third_held_key[1]
    target = param["event"].text() or chr(param["event"].key())
    source_pair = surrounding_chars(source)
    target_pair = surrounding_chars(target)
    if not source_pair or not target_pair:
        return cursor

    text = cursor.document().toPlainText()
    encoded_text = text.encode("utf-16-le")
    position = len(encoded_text[: cursor.position() * 2].decode("utf-16-le"))
    bounds = find_surrounding(text, position, source_pair)
    if bounds is None:
        return cursor

    start, end = bounds
    content_start = start + 1
    content = text[content_start:end]
    offset = max(0, position - start - 1)
    if source in "([{<":
        offset -= len(content) - len(content.lstrip())
        content = content.strip()
    offset = min(max(0, offset), len(content))

    padding = " " if target in ("(", "[", "{") else ""
    left_char, right_char = target_pair
    prefix = left_char + padding
    replacement = prefix + content + padding + right_char
    start_position = len(text[:start].encode("utf-16-le")) // 2
    end_position = len(text[:end].encode("utf-16-le")) // 2 + 1
    offset = len((prefix + content[:offset]).encode("utf-16-le")) // 2

    cursor.beginEditBlock()
    cursor.setPosition(start_position)
    cursor.setPosition(end_position, QTextCursor.KeepAnchor)
    cursor.insertText(replacement)
    cursor.setPosition(start_position + offset)
    cursor.endEditBlock()
    return cursor
