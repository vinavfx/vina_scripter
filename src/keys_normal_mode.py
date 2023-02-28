# All these functions were taken from the 'ksscripteditor.py' script from Adrian Pueyo's 'Knob Scripter' editor.
# This script was modified by Francisco Contreras.

import re
from PySide2.QtCore import Qt
from PySide2.QtGui import  QTextCursor
from PySide2.QtWidgets import QPlainTextEdit


def key_press_event(self, event):

    key = event.key()
    ctrl = bool(event.modifiers() & Qt.ControlModifier)
    shift = bool(event.modifiers() & Qt.ShiftModifier)
    alt = event.modifiers() == Qt.AltModifier
    pre_scroll = self.verticalScrollBar().value()

    if alt and key == Qt.Key_1:
        self.parent.parent.set_script_page(0)
        return

    elif alt and key == Qt.Key_2:
        self.parent.parent.set_script_page(1)
        return

    elif alt and key == Qt.Key_3:
        self.parent.parent.set_script_page(2)
        return

    elif key == Qt.Key_Escape:
        self.parent.parent.exit_node()
        return

    up_arrow = 16777235
    down_arrow = 16777237

    # if Tab convert to Space
    if key == 16777217:
        indentation(self, 'indent')

    # if Shift+Tab remove indent
    elif key == 16777218:
        indentation(self, 'unindent')

    # if BackSpace try to snap to previous indent level
    elif key == 16777219:
        if not unindentBackspace(self):
            QPlainTextEdit.keyPressEvent(self, event)
    else:
        # COOL BEHAVIORS SIMILAR TO SUBLIME GO NEXT!
        cursor = self.textCursor()
        cpos = cursor.position()
        apos = cursor.anchor()
        text_before_cursor = self.toPlainText()[:min(cpos, apos)]
        text_after_cursor = self.toPlainText()[max(cpos, apos):]
        text_all = self.toPlainText()
        to_line_start = text_before_cursor[::-1].find("\n")
        if to_line_start == -1:
            # Position of the start of the line that includes the cursor selection start
            linestart_pos = 0
        else:
            linestart_pos = len(text_before_cursor) - to_line_start

        to_line_end = text_after_cursor.find("\n")
        if to_line_end == -1:
            # Position of the end of the line that includes the cursor selection end
            lineend_pos = len(text_all)
        else:
            lineend_pos = max(cpos, apos) + to_line_end

        text_before_lines = text_all[:linestart_pos]
        text_after_lines = text_all[lineend_pos:]
        if len(text_after_lines) and text_after_lines.startswith("\n"):
            text_after_lines = text_after_lines[1:]
        text_lines = text_all[linestart_pos:lineend_pos]

        if cursor.hasSelection():
            selection = cursor.selection().toPlainText()
        else:
            selection = ""
        if key == Qt.Key_ParenLeft and (len(selection) > 0 or re.match(r"[\s)}\];]+", text_after_cursor) or not len(
                text_after_cursor)):  # (
            cursor.insertText("(" + selection + ")")
            cursor.setPosition(apos + 1, QTextCursor.MoveAnchor)
            cursor.setPosition(cpos + 1, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        # )
        elif key == Qt.Key_ParenRight and text_after_cursor.startswith(")"):
            cursor.movePosition(QTextCursor.NextCharacter)
            self.setTextCursor(cursor)
        elif key in [94, Qt.Key_BracketLeft] \
                and (len(selection) > 0 or re.match(r"[\s)}\];]+", text_after_cursor)
                     or not len(text_after_cursor)):  # [
            cursor.insertText("[" + selection + "]")
            cursor.setPosition(apos + 1, QTextCursor.MoveAnchor)
            cursor.setPosition(cpos + 1, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        # ]
        elif key in [Qt.Key_BracketRight, 43, 93] and text_after_cursor.startswith("]"):
            cursor.movePosition(QTextCursor.NextCharacter)
            self.setTextCursor(cursor)
        elif key == Qt.Key_BraceLeft and (len(selection) > 0 or re.match(r"[\s)}\];]+", text_after_cursor)
                                          or not len(text_after_cursor)):  # {
            cursor.insertText("{" + selection + "}")
            cursor.setPosition(apos + 1, QTextCursor.MoveAnchor)
            cursor.setPosition(cpos + 1, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        # }
        elif key in [199, Qt.Key_BraceRight] and text_after_cursor.startswith("}"):
            cursor.movePosition(QTextCursor.NextCharacter)
            self.setTextCursor(cursor)
        elif key == 34:  # "
            if len(selection) > 0:
                cursor.insertText('"' + selection + '"')
                cursor.setPosition(apos + 1, QTextCursor.MoveAnchor)
                cursor.setPosition(cpos + 1, QTextCursor.KeepAnchor)
            elif text_after_cursor.startswith('"') and '"' in text_before_cursor.split("\n")[-1]:
                cursor.movePosition(QTextCursor.NextCharacter)
            # If chars after cursor, act normal
            elif not re.match(r"(?:[\s)\]]+|$)", text_after_cursor):
                QPlainTextEdit.keyPressEvent(self, event)
            elif not re.search(r"[\s.({\[,]$",
                               text_before_cursor) and text_before_cursor != "":  # Chars before cursor: act normal
                QPlainTextEdit.keyPressEvent(self, event)
            else:
                cursor.insertText('"' + selection + '"')
                cursor.setPosition(apos + 1, QTextCursor.MoveAnchor)
                cursor.setPosition(cpos + 1, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        elif key == 39:  # '
            if len(selection) > 0:
                cursor.insertText("'" + selection + "'")
                cursor.setPosition(apos + 1, QTextCursor.MoveAnchor)
                cursor.setPosition(cpos + 1, QTextCursor.KeepAnchor)
            elif text_after_cursor.startswith("'") and "'" in text_before_cursor.split("\n")[-1]:
                cursor.movePosition(QTextCursor.NextCharacter)
            # If chars after cursor, act normal
            elif not re.match(r"(?:[\s)\]]+|$)", text_after_cursor):
                QPlainTextEdit.keyPressEvent(self, event)
            elif not re.search(r"[\s.({\[,]$",
                               text_before_cursor) and text_before_cursor != "":  # Chars before cursor: act normal
                QPlainTextEdit.keyPressEvent(self, event)
            else:
                cursor.insertText("'" + selection + "'")
                cursor.setPosition(apos + 1, QTextCursor.MoveAnchor)
                cursor.setPosition(cpos + 1, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        elif key == 35 and len(selection):  # # (yes, a hash)
            # If there's a selection, insert a hash at the start of each line.. how?
            if selection != "":
                selection_split = selection.split("\n")
                if all(i.startswith("#") for i in selection_split):
                    selection_commented = "\n".join(
                        [s[1:] for s in selection_split])  # Uncommented
                else:
                    selection_commented = "#" + "\n#".join(selection_split)
                cursor.insertText(selection_commented)
                if apos > cpos:
                    cursor.setPosition(apos + len(selection_commented) - len(selection),
                                       QTextCursor.MoveAnchor)
                    cursor.setPosition(cpos, QTextCursor.KeepAnchor)
                else:
                    cursor.setPosition(apos, QTextCursor.MoveAnchor)
                    cursor.setPosition(cpos + len(selection_commented) - len(selection),
                                       QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)

        elif key == 68 and ctrl and shift:  # Ctrl+Shift+D, to duplicate text or line/s

            if not len(selection):
                self.setPlainText(
                    text_before_lines + text_lines + "\n" + text_lines + "\n" + text_after_lines)
                cursor.setPosition(
                    apos + len(text_lines) + 1, QTextCursor.MoveAnchor)
                cursor.setPosition(
                    cpos + len(text_lines) + 1, QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
                self.verticalScrollBar().setValue(pre_scroll)
                scrollToCursor(self)
            else:
                if text_before_cursor.endswith("\n") and not selection.startswith("\n"):
                    cursor.insertText(selection + "\n" + selection)
                    cursor.setPosition(
                        apos + len(selection) + 1, QTextCursor.MoveAnchor)
                    cursor.setPosition(
                        cpos + len(selection) + 1, QTextCursor.KeepAnchor)
                else:
                    cursor.insertText(selection + selection)
                    cursor.setPosition(
                        apos + len(selection), QTextCursor.MoveAnchor)
                    cursor.setPosition(
                        cpos + len(selection), QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)

        elif key == up_arrow and ctrl and shift and len(
                text_before_lines):  # Ctrl+Shift+Up, to move the selected line/s up
            prev_line_start_distance = text_before_lines[:-1][::-1].find(
                "\n")
            if prev_line_start_distance == -1:
                prev_line_start_pos = 0  # Position of the start of the previous line
            else:
                prev_line_start_pos = len(
                    text_before_lines) - 1 - prev_line_start_distance
            prev_line = text_before_lines[prev_line_start_pos:]

            text_before_prev_line = text_before_lines[:prev_line_start_pos]

            if prev_line.endswith("\n"):
                prev_line = prev_line[:-1]

            if len(text_after_lines):
                text_after_lines = "\n" + text_after_lines

            self.setPlainText(
                text_before_prev_line + text_lines + "\n" + prev_line + text_after_lines)
            cursor.setPosition(apos - len(prev_line) -
                               1, QTextCursor.MoveAnchor)
            cursor.setPosition(cpos - len(prev_line) -
                               1, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
            self.verticalScrollBar().setValue(pre_scroll)
            scrollToCursor(self)
            return

        elif key == down_arrow and ctrl and shift:  # Ctrl+Shift+Up, to move the selected line/s up
            if not len(text_after_lines):
                text_after_lines = ""
            next_line_end_distance = text_after_lines.find("\n")
            if next_line_end_distance == -1:
                next_line_end_pos = len(text_all)
            else:
                next_line_end_pos = next_line_end_distance
            next_line = text_after_lines[:next_line_end_pos]
            text_after_next_line = text_after_lines[next_line_end_pos:]

            self.setPlainText(text_before_lines + next_line +
                              "\n" + text_lines + text_after_next_line)
            cursor.setPosition(apos + len(next_line) +
                               1, QTextCursor.MoveAnchor)
            cursor.setPosition(cpos + len(next_line) +
                               1, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
            self.verticalScrollBar().setValue(pre_scroll)
            scrollToCursor(self)
            return

        # If up key and nothing happens, go to start
        elif key == up_arrow and not len(text_before_lines):
            if not shift:
                cursor.setPosition(0, QTextCursor.MoveAnchor)
                self.setTextCursor(cursor)
            else:
                cursor.setPosition(0, QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)

        # If up key and nothing happens, go to start
        elif key == down_arrow and not len(text_after_lines):
            if not shift:
                cursor.setPosition(len(text_all), QTextCursor.MoveAnchor)
                self.setTextCursor(cursor)
            else:
                cursor.setPosition(len(text_all), QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)

        # if enter or return, match indent level
        elif key in [16777220, 16777221]:
            indentNewLine(self)

        # If ctrl + +, increase font size
        elif ctrl and key == Qt.Key_Plus:
            font = self.font()
            font.setPointSize(-(-font.pointSize() // 0.9))
            self.setFont(font)
        # If ctrl + -, decrease font size
        elif ctrl and key == Qt.Key_Minus:
            font = self.font()
            font.setPointSize(font.pointSize() // 1.1)
            self.setFont(font)

        else:
            QPlainTextEdit.keyPressEvent(self, event)

    scrollToCursor(self)


def indentNewLine(self):
    # In case selection covers multiple line, make it one line first
    self.insertPlainText('')
    getCursorInfo(self)

    # Check how many spaces after cursor
    text = self.document().findBlock(self.firstChar).text()
    text_in_front = text[:self.cursorBlockPos]

    if len(text_in_front) == 0:
        self.insertPlainText('\n')
        return

    indent_level = 0
    for i in text_in_front:
        if i == ' ':
            indent_level += 1
        else:
            break

    indent_level /= self.tab_spaces

    # find out whether text_in_front's last character was a ':'
    # if that's the case add another indent.
    # ignore any spaces at the end, however also
    # make sure text_in_front is not just an indent
    if text_in_front.count(' ') != len(text_in_front):
        while text_in_front[-1] == ' ':
            text_in_front = text_in_front[:-1]

    if text_in_front[-1] == ':':
        indent_level += 1

    # new line
    self.insertPlainText('\n')
    # match indent
    self.insertPlainText(' ' * int(self.tab_spaces * indent_level))


def getCursorInfo(self):

    self.cursor = self.textCursor()

    self.firstChar = self.cursor.selectionStart()
    self.lastChar = self.cursor.selectionEnd()

    self.noSelection = False
    if self.firstChar == self.lastChar:
        self.noSelection = True

    self.originalPosition = self.cursor.position()
    self.cursorBlockPos = self.cursor.positionInBlock()


def scrollToCursor(self):
    self.cursor = self.textCursor()
    self.cursor.movePosition(
        QTextCursor.NoMove)  # Does nothing, but makes the scroll go to the right place...
    self.setTextCursor(self.cursor)


def indentation(self, mode):

    pre_scroll = self.verticalScrollBar().value()
    getCursorInfo(self)

    # if nothing is selected and mode is set to indent, simply insert as many
    # space as needed to reach the next indentation level.
    if self.noSelection and mode == 'indent':
        remaining_spaces = self.tab_spaces - \
            (self.cursorBlockPos % self.tab_spaces)
        self.insertPlainText(' ' * remaining_spaces)
        return

    selected_blocks = findBlocks(self, self.firstChar, self.lastChar)
    before_blocks = findBlocks(
        self, last=self.firstChar - 1, exclude=selected_blocks)
    after_blocks = findBlocks(
        self, first=self.lastChar + 1, exclude=selected_blocks)

    before_blocks_text = blocks2list(self, before_blocks)
    selected_blocks_text = blocks2list(self, selected_blocks, mode)
    after_blocks_text = blocks2list(self, after_blocks)

    combined_text = '\n'.join(
        before_blocks_text + selected_blocks_text + after_blocks_text)

    # make sure the line count stays the same
    original_block_count = len(self.toPlainText().split('\n'))
    combined_text = '\n'.join(combined_text.split('\n')[
                              :original_block_count])

    self.clear()
    self.setPlainText(combined_text)

    if self.noSelection:
        self.cursor.setPosition(self.lastChar)

    # check whether the the orignal selection was from top to bottom or vice versa
    else:
        if self.originalPosition == self.firstChar:
            first = self.lastChar
            last = self.firstChar
            first_block_snap = QTextCursor.EndOfBlock
            last_block_snap = QTextCursor.StartOfBlock
        else:
            first = self.firstChar
            last = self.lastChar
            first_block_snap = QTextCursor.StartOfBlock
            last_block_snap = QTextCursor.EndOfBlock

        self.cursor.setPosition(first)
        self.cursor.movePosition(first_block_snap, QTextCursor.MoveAnchor)
        self.cursor.setPosition(last, QTextCursor.KeepAnchor)
        self.cursor.movePosition(last_block_snap, QTextCursor.KeepAnchor)

    self.setTextCursor(self.cursor)
    self.verticalScrollBar().setValue(pre_scroll)


def unindentBackspace(self):
    getCursorInfo(self)

    if not self.noSelection or self.cursorBlockPos == 0:
        return False

    # check text in front of cursor
    text_in_front = self.document().findBlock(
        self.firstChar).text()[:self.cursorBlockPos]

    # check whether solely spaces
    if text_in_front != ' ' * self.cursorBlockPos:
        return False

    # snap to previous indent level
    spaces = len(text_in_front)

    for _ in range(int(spaces - int(float(spaces - 1) / self.tab_spaces) * self.tab_spaces - 1)):
        self.cursor.deletePreviousChar()


def findBlocks(self, first=0, last=None, exclude=None):
    exclude = exclude or []
    blocks = []
    if last is None:
        last = self.document().characterCount()
    for pos in range(first, last + 1):
        block = self.document().findBlock(pos)
        if block not in blocks and block not in exclude:
            blocks.append(block)
    return blocks


def blocks2list(self, blocks, mode=None):
    text = []
    for block in blocks:
        block_text = block.text()
        if mode == 'unindent':
            if block_text.startswith(' ' * self.tab_spaces):
                block_text = block_text[self.tab_spaces:]
                self.lastChar -= self.tab_spaces
            elif block_text.startswith(' '):
                block_text = block_text[1:]
                self.lastChar -= 1

        elif mode == 'indent':
            block_text = ' ' * self.tab_spaces + block_text
            self.lastChar += self.tab_spaces

        text.append(block_text)

    return text
