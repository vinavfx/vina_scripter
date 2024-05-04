# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
from PySide2.QtGui import QTextCursor


def redo(self, cursor, _):
    self.document().redo()
    return cursor


def undo(self, cursor, _):
    self.document().undo()
    return cursor


def insert_next_char(self, cursor, _):
    cursor.movePosition(QTextCursor.Right)
    self.set_mode('insert')

    return cursor


def zoom(self, _, __, increase=True):
    if increase:
        font = self.font()
        size = font.pointSize() + 1
        font.setPointSize(size)
        self.setFont(font)
    else:
        font = self.font()
        size = font.pointSize() - 1
        font.setPointSize(size)
        self.setFont(font)


def insert(self, cursor, _):
    self.set_mode('insert')
    return cursor


def insert_and_delete_char(self, cursor, _):
    cursor.deleteChar()
    self.set_mode('insert')
    return cursor


def insert_under(self, cursor, _):
    cursor.beginEditBlock()
    cursor.select(QTextCursor.LineUnderCursor)
    line = cursor.selectedText().strip()
    first_word = line.split()[0] if line.split() else ''
    first_word = ''.join(c for c in first_word if c.isalpha())
    spaces = 0

    if first_word in self.key_words:
        spaces += self.tab_spaces

    cursor.select(QTextCursor.BlockUnderCursor)
    if not cursor.selectedText().strip() == '':
        cursor.movePosition(QTextCursor.StartOfLine)
        while cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor) and cursor.selectedText().isspace():
            spaces += 1

    cursor.movePosition(QTextCursor.EndOfLine)
    cursor.insertBlock()
    cursor.insertText(' ' * spaces)

    self.setTextCursor(cursor)
    self.set_mode('insert')
    cursor.endEditBlock()

    return cursor


def strip_text(cursor):
    text = cursor.block().text()
    new_text = text.rstrip()

    cursor.select(QTextCursor.LineUnderCursor)
    cursor.removeSelectedText()

    if new_text:
        cursor.insertText(new_text)
    else:
        cursor.movePosition(QTextCursor.StartOfLine)


def normal(self, cursor, _=None):
    self.set_mode('normal')

    text = cursor.block().text()
    new_text = text.rstrip()

    if not text == new_text:
        cursor.beginEditBlock()
        strip_text(cursor)
        cursor.endEditBlock()

    cursor.clearSelection()
    self.setTextCursor(cursor)

    return False


def insert_to_end(self, cursor, _):
    cursor.movePosition(QTextCursor.EndOfLine)
    self.set_mode('insert')
    return cursor


def insert_to_start(self, cursor, _):
    cursor.movePosition(QTextCursor.StartOfLine)
    block_text = cursor.block().text()
    if block_text[0].isspace() if block_text else '':
        cursor.movePosition(QTextCursor.NextWord)
    self.set_mode('insert')
    return cursor


def raise_bottom_line(_, cursor, __):
    old_position = cursor.position()
    cursor.beginEditBlock()
    cursor.movePosition(QTextCursor.Down)
    cursor.select(QTextCursor.BlockUnderCursor)
    down_text = cursor.selectedText().strip()
    cursor.removeSelectedText()
    cursor.insertText(' ' + down_text)
    cursor.endEditBlock()
    cursor.setPosition(old_position)
    return cursor


def visual(self, cursor, _):
    self.set_mode('visual')
    return cursor


def visual_line(self, cursor, _):
    cursor.movePosition(QTextCursor.StartOfLine)
    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    self.set_mode('visual_line')
    return cursor


def write_command(self, cursor, _):
    self.parent.parent.vim.write_command(':')
    return cursor


def escape(self, cursor, _):
    self.parent.editor.highlight_word_clean()
    return cursor
