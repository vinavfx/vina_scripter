# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
from PySide2.QtGui import QTextCursor


def search(self, cursor, _):
    self.parent.parent.vim.write_command('/')
    return cursor


def find_words_over_cursor(self, cursor, _):
    old_position = cursor.position()
    cursor.movePosition(QTextCursor.StartOfWord)
    cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
    word = cursor.selectedText()
    cursor.clearSelection()
    self.parent.editor.is_search = False
    self.parent.editor.highlight_word(word)
    cursor.setPosition(old_position)

    return cursor


def next_found_word(self, cursor, _):
    words = self.parent.editor.get_words()
    pos = cursor.position()

    if words:
        close_position = min(words, key=lambda x: abs(x - pos))
        index = words.index(close_position)
        next_word_pos = words[index]

        if next_word_pos <= pos:
            index += 1
            next_word_pos = words[index] if index < len(
                words) else words[0]

        cursor.setPosition(next_word_pos)

    self.parent.editor.highlight_word(None, cursor)
    return cursor


def previous_found_word(self, cursor, _):
    words = self.parent.editor.get_words()
    pos = cursor.position()

    if words:
        close_position = min(words, key=lambda x: abs(x - pos))
        index = words.index(close_position)
        prev_word_pos = words[index]

        if prev_word_pos >= pos:
            index -= 1
            prev_word_pos = words[index]

        cursor.setPosition(prev_word_pos)

    self.parent.editor.highlight_word(None, cursor)
    return cursor
