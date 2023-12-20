# -----------------------------------------------------------
# AUTHOR --------> Francisco Jose Contreras Cuevas
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
from PySide2.QtGui import QTextCursor
from PySide2.QtCore import Qt

from .vim_nav_actions import *
from .vim_general_actions import strip_text


def delete_towards(self, cursor, param):
    key = param['key'].lower()
    param['anchor'] = QTextCursor.KeepAnchor
    shift = param['event'].modifiers() == Qt.ShiftModifier

    cursor.beginEditBlock()

    if shift and key == 'd':
        goto_end_of_line(self, cursor, param, True)

    elif key == 'd':
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, param['anchor'])

    else:
        select_towards(self, cursor, param)

    text = cursor.selectedText()
    cursor.removeSelectedText()

    multiline = False

    if shift and key == 'd':
        strip_text(cursor)

    elif key in ['d', 'k', 'j']:
        multiline = True
        cursor.deleteChar()
        if cursor.block().text().strip():
            cursor.movePosition(QTextCursor.NextWord)

    self.copied = (text, multiline)

    cursor.endEditBlock()
    return cursor


def delete_towards_and_insert(self, cursor, param):
    key = param['key'].lower()
    param['anchor'] = QTextCursor.KeepAnchor
    shift = param['event'].modifiers() == Qt.ShiftModifier

    cursor.beginEditBlock()

    if shift and key == 'c':
        goto_end_of_line(self, cursor, param, True)

    elif key == 'c':
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, param['anchor'])

        text = cursor.block().text()
        first_char = text[0] if text else ''

        if not first_char.isspace():
            cursor.removeSelectedText()
        else:
            cursor.clearSelection()
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.movePosition(QTextCursor.StartOfLine,
                                QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.NextWord, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
    else:
        select_towards(self, cursor, param)

    cursor.removeSelectedText()
    cursor.endEditBlock()

    self.set_mode('insert')


def delete_selection(self, cursor, param):
    key = param['key']

    text = cursor.selectedText()
    multiline = True if len(text.splitlines()) > 1 else False
    self.copied = (text, multiline)

    cursor.beginEditBlock()
    cursor.removeSelectedText()
    if cursor.selectionEnd() - cursor.selectionStart() == cursor.block().length() - 1:
        cursor.deleteChar()

    cursor.endEditBlock()

    if key == 'd':
        self.set_mode('normal')
    elif key == 'c':
        self.set_mode('insert')


def delete_char(_, cursor, __):
    cursor.deleteChar()
    return cursor


def copy(self, cursor, param):
    key = param['key'].lower()
    param['anchor'] = QTextCursor.KeepAnchor

    pos = cursor.position()

    if key == 'y':
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, param['anchor'])
    else:
        select_towards(self, cursor, param)

    text = cursor.selectedText()
    multiline = True if len(text.splitlines()) > 1 else False

    if key == 'y':
        multiline = True

    self.copied = (cursor.selectedText(), multiline)

    cursor.clearSelection()
    cursor.setPosition(pos)

    return cursor


def copy_selection(self, cursor, _):

    text = cursor.selectedText()
    multiline = True if len(text.splitlines()) > 1 else False

    self.copied = (text, multiline)
    self.set_mode('normal')
    cursor.clearSelection()
    self.setTextCursor(cursor)


def paste(self, cursor, _):
    if not self.copied:
        return

    cursor.beginEditBlock()
    text, multiline = self.copied

    for _ in range(self.held_number):
        if multiline:
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertBlock()

        cursor.insertText(text)

        if multiline:
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.NextWord)

    cursor.endEditBlock()

    return cursor


def replace_char(_, cursor, param):
    event = param['event']

    char = chr(event.key())
    shift = event.modifiers() == Qt.ShiftModifier

    cursor.beginEditBlock()
    _char = char.upper() if shift else char.lower()

    text = cursor.block().text()

    if text.strip():
        cursor.deleteChar()
        cursor.insertText(_char)
        cursor.movePosition(QTextCursor.Left)

    cursor.endEditBlock()
    return cursor
