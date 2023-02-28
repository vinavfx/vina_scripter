# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
from PySide2.QtGui import QTextCursor

from .vim_common_actions import fill_selection_blocks
from .vim_nav_actions import go_to_first_char


def comment_current_line(self, cursor, _, toggle=True, comment=None):
    cursor.beginEditBlock()

    cursor.movePosition(QTextCursor.StartOfLine)
    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

    text = cursor.selectedText()
    cursor.removeSelectedText()

    commented_text = comment_text(self, text, toggle, comment)

    cursor.insertText(commented_text)
    go_to_first_char(cursor)
    cursor.endEditBlock()

    self.setTextCursor(cursor)

    return False


def comment_syntax(self):
    if self.parent.parent.python_syntax:
        char_comment = '#'
    else:
        char_comment = '//'

    return char_comment


def comment_selected_text(self, cursor, _, toggle=True, comment=None):
    cursor.beginEditBlock()

    cursor = fill_selection_blocks(cursor)
    start = cursor.selectionStart()

    text = cursor.selectedText()

    start = cursor.selectionStart()
    cursor.setPosition(start)

    for _ in text.splitlines():
        cursor.select(QTextCursor.BlockUnderCursor)
        text_line = cursor.selectedText()
        cursor.removeSelectedText()

        commented_text = comment_text(self, text_line, toggle, comment)
        cursor.insertText(commented_text)
        cursor.movePosition(QTextCursor.Down)

    cursor.endEditBlock()

    cursor.clearSelection()
    self.set_mode('normal')

    cursor.setPosition(start)
    go_to_first_char(cursor)

    self.setTextCursor(cursor)

    return False


def comment_end_line(self, cursor, _):
    cursor.movePosition(QTextCursor.EndOfLine)
    cursor.insertText(' {} '.format(comment_syntax(self)))

    self.set_mode('insert')

    return cursor


def comment_to_end(self, cursor, __):
    cursor.insertText('{} '.format(comment_syntax(self)))
    return cursor


def comment_text(self, text, toggle=True, comment=None):
    if not text.strip():
        return

    char_comment = comment_syntax(self)

    new_text = ''
    for line in text.splitlines():

        init_spaces = line[:len(line)-len(line.lstrip())]
        first_char_index = next(
            (i for i, c in enumerate(line) if not c.isspace()), 0)

        first_char = line[first_char_index] if first_char_index < len(
            line) else ''
        second_char = line[first_char_index +
                           1] if first_char_index + 1 < len(line) else ''

        comment_char = first_char
        if '//' in char_comment:
            comment_char = first_char + second_char

        if toggle:
            comment = not comment_char == char_comment

        if comment:
            if line.strip():
                new_text += '{}{} {}\n'.format(init_spaces,
                                               char_comment, line.strip())
            else:
                new_text += '\n'
        else:
            new_line = line.strip().lstrip(char_comment).rstrip().strip()
            new_text += init_spaces + new_line + '\n'


    new_text = new_text[:-1]

    return new_text

