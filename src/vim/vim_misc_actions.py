# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
from PySide2.QtGui import QTextCursor

from .vim_general_actions import normal


def change_case(self, cursor, _, uppercase=True):
    cursor.beginEditBlock()

    if uppercase:
        text = cursor.selectedText().upper()
    else:
        text = cursor.selectedText().lower()

    cursor.removeSelectedText()
    cursor.insertText(text)
    cursor.endEditBlock()

    self.setTextCursor(cursor)
    normal(self, cursor)


def change_case_word(_, cursor, __, uppercase=True):
    pos = cursor.position()
    cursor.beginEditBlock()
    cursor.select(QTextCursor.WordUnderCursor)

    if uppercase:
        text = cursor.selectedText().upper()
    else:
        text = cursor.selectedText().lower()

    cursor.removeSelectedText()
    cursor.insertText(text)
    cursor.endEditBlock()
    cursor.setPosition(pos)
    return cursor


def indent_line_to_left(self, cursor, _, edit_block=True):
    if edit_block:
        cursor.beginEditBlock()
    text = cursor.block().text()

    cursor.movePosition(QTextCursor.StartOfLine)

    for c in text[:self.tab_spaces]:
        if c.isspace():
            cursor.deleteChar()
        else:
            break

    text = cursor.block().text()

    if text[0].isspace() if text else '':
        cursor.movePosition(QTextCursor.NextWord)

    if edit_block:
        cursor.endEditBlock()

    return cursor


def indent_line_to_right(self, cursor, _, edit_block=True):
    if edit_block:
        cursor.beginEditBlock()

    if cursor.block().text().strip():
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.insertText(self.tab_string)

        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.NextWord)

    if edit_block:
        cursor.endEditBlock()
    return cursor


def indent_selection(self, cursor, _, right=True):
    start = cursor.selectionStart()
    end = cursor.selectionEnd()

    cursor.beginEditBlock()

    cursor.setPosition(start)
    block1 = cursor.blockNumber()
    cursor.setPosition(end)
    block2 = cursor.blockNumber()

    cursor.setPosition(start)

    for _ in range(block1, block2 + 1):
        for _ in range(self.held_number):
            if right:
                indent_line_to_right(self, cursor, _, False)
            else:
                indent_line_to_left(self, cursor, _, False)

        cursor.movePosition(QTextCursor.NextBlock)

    cursor.clearSelection()
    self.set_mode('normal')

    cursor.setPosition(start)
    cursor.movePosition(QTextCursor.StartOfLine)

    text = cursor.block().text()
    if text[0].isspace() if text else '':
        cursor.movePosition(QTextCursor.NextWord)

    cursor.endEditBlock()

    self.setTextCursor(cursor)
