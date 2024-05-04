# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
from PySide2.QtGui import QTextCursor


def enclose_word(_, cursor, param):
    char = chr(param['event'].key())

    left_char = char
    right_char = char

    if char in ['(', ')']:
        left_char = '('
        right_char = ')'

    elif char in ['[', ']']:
        left_char = '['
        right_char = ']'

    elif char in ['{', '}']:
        left_char = '{'
        right_char = '}'

    pos = cursor.position()
    cursor.beginEditBlock()

    cursor.select(QTextCursor.WordUnderCursor)
    text = cursor.selectedText()

    cursor.removeSelectedText()

    new_text = '{}{}{}'.format(left_char, text, right_char)
    cursor.insertText(new_text)
    cursor.setPosition(pos + 1)

    cursor.endEditBlock()

    return cursor


def get_enclosing_word(cursor):
    cursor.select(QTextCursor.WordUnderCursor)
    word = cursor.selectedText()

    # Aqui retornar los signos que encierren una
    # palabra o frase para usarlos
    # en las 2 funciones de abajo


def remove_enclosed_word(_, cursor, param):
    char = chr(param['event'].key())
    return cursor


def replace_enclosed_word(self, cursor, param):
    prev_char = self.third_held_key[1]
    char = chr(param['event'].key())

    get_enclosing_word(cursor)

    return cursor
