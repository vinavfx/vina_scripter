# -----------------------------------------------------------
# AUTHOR --------> Francisco Jose Contreras Cuevas
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import ast
import traceback

from PySide2.QtGui import QTextCursor
from PySide2.QtCore import Qt

from .vim_common_actions import fill_selection_blocks


def select_towards(self, cursor, param):
    key = param['key'].lower()
    second_key = param['hotkey']['second_key']
    shift = param['event'].modifiers() == Qt.ShiftModifier

    param['anchor'] = QTextCursor.KeepAnchor

    if shift and key == 'g':
        goto_end(self, cursor, param)
        fill_selection_blocks(cursor)

    elif key == 'g' and second_key == 'g':
        goto_start(self, cursor, param)
        fill_selection_blocks(cursor)

    elif key == '0':
        goto_start_of_line(self, cursor, param)

    elif key == '_':
        goto_first_char(self, cursor, param)

    elif key == '$':
        goto_end_of_line(self, cursor, param, True)

    elif key == '?':
        goto_char(self, cursor, param, second_key.isupper(), True)

    elif key == 'b':
        go_back_word_start(self, cursor, param)

    elif key == 'e' or key == 'w':
        goto_end_of_word(self, cursor, param, True)

    elif key == 'l':
        goto_right(self, cursor, param)

    elif key == 'h':
        goto_left(self, cursor, param)

    elif key == 'k':
        goto_up(self, cursor, param)
        fill_selection_blocks(cursor)

    elif key == 'j':
        goto_down(self, cursor, param)
        fill_selection_blocks(cursor)

    return cursor


def goto_start(_, cursor, param):
    cursor.movePosition(QTextCursor.Start, param['anchor'])
    return cursor


def goto_end(_, cursor, param):
    cursor.movePosition(QTextCursor.End, param['anchor'])
    return cursor


def goto_char(_, cursor, param, reverse=False, forward=False):
    event = param['event']
    anchor = param['anchor']

    try:
        char = chr(event.key())
    except:
        char = ''

    text = cursor.block().text()
    if not text:
        return cursor

    pos = cursor.positionInBlock()
    shift = event.modifiers() == Qt.ShiftModifier

    _char = char.upper() if shift else char.lower()
    if not _char:
        return cursor

    to_move = 0
    finded = False

    if reverse:
        text = text[:pos][::-1]
        pos = len(text) - pos - 1
    elif forward:
        pos -= 1

    for i in range(pos, len(text)):
        if text[i] == _char and not i == pos:
            finded = True
            break
        to_move += 1

    if finded:
        if reverse:
            for _ in range(to_move):
                cursor.movePosition(QTextCursor.Left, anchor)
        else:
            for _ in range(to_move):
                cursor.movePosition(QTextCursor.Right, anchor)

    return cursor


def goto_end_of_line(_, cursor, param, forward=False):
    anchor = param['anchor']
    cursor.movePosition(QTextCursor.EndOfLine, anchor)
    if not forward:
        cursor.movePosition(QTextCursor.Left, anchor)
    return cursor


def go_to_first_char(cursor, anchor=QTextCursor.MoveAnchor):

    cursor.movePosition(QTextCursor.StartOfLine, anchor)
    block_text = cursor.block().text()

    if block_text[0].isspace() if block_text else '':
        cursor.movePosition(QTextCursor.NextWord, anchor)

    return cursor


def goto_first_char(_, cursor, param):
    go_to_first_char(cursor, param['anchor'])
    return cursor


def goto_end_of_word(_, cursor, param, forward=False):
    anchor = param['anchor']

    text = cursor.block().text()
    pos = cursor.positionInBlock()
    current_char = text[pos] if len(text) > pos else ''

    pos = cursor.position()

    if current_char.isspace():
        cursor.movePosition(QTextCursor.NextWord, anchor)

    if forward:
        cursor.movePosition(QTextCursor.EndOfWord, anchor)
        if pos == cursor.position():
            cursor.movePosition(QTextCursor.Down, anchor)
            cursor.movePosition(QTextCursor.StartOfLine, anchor)
    else:
        cursor.movePosition(QTextCursor.Right, anchor)
        cursor.movePosition(QTextCursor.EndOfWord, anchor)
        cursor.movePosition(QTextCursor.Left, anchor)

        if pos == cursor.position():
            cursor.movePosition(QTextCursor.Right, anchor, 2)
            cursor.movePosition(QTextCursor.EndOfWord, anchor)
            cursor.movePosition(QTextCursor.Left, anchor)

    return cursor


def goto_start_of_line(_, cursor, param):
    anchor = param['anchor']
    cursor.movePosition(QTextCursor.StartOfLine, anchor)
    return cursor


def goto_next_word_start(_, cursor, param):
    anchor = param['anchor']
    cursor.movePosition(QTextCursor.NextWord, anchor)
    return cursor


def go_back_word_start(_, cursor, param):
    anchor = param['anchor']
    cursor.movePosition(QTextCursor.Left, anchor)
    cursor.movePosition(QTextCursor.StartOfWord, anchor)
    return cursor


def goto_up(self, cursor, param):
    cursor.movePosition(QTextCursor.Up, param['anchor'], self.held_number)
    return cursor


def goto_down(self, cursor, param):
    anchor = param['anchor']
    cursor.movePosition(QTextCursor.Down, anchor, self.held_number)
    return cursor


def goto_left(self, cursor, param):
    anchor = param['anchor']
    if cursor.positionInBlock() > 0:
        cursor.movePosition(QTextCursor.Left, anchor, self.held_number)

    return cursor


def goto_right(self, cursor, param):
    anchor = param['anchor']
    if cursor.positionInBlock() < cursor.block().length() - 1:
        cursor.movePosition(QTextCursor.Right, anchor, self.held_number)

    return cursor


def scroll_down(self, _, __):
    scroll_bar = self.verticalScrollBar()
    current_position = scroll_bar.value()
    scroll_bar.setValue(current_position + 10)
    self.number_area.update()


def scroll_up(self, _, __):

    scroll_bar = self.verticalScrollBar()
    current_position = scroll_bar.value()
    scroll_bar.setValue(current_position - 10)
    self.number_area.update()


def center_cursor(self, cursor, _=None):
    block_height = self.document().documentLayout(
    ).blockBoundingRect(cursor.block()).height()

    visible_rect = self.visibleRegion().boundingRect()
    middle_block = int((visible_rect.center().y() -
                       block_height/2) / block_height)

    scroll_bar = self.verticalScrollBar()
    current_block = cursor.blockNumber()

    scroll_bar.setValue(current_block - middle_block)

    return cursor


def jump_up(_, cursor, param):
    cursor.movePosition(QTextCursor.Up, param['anchor'], 10)
    return cursor


def jump_down(_, cursor, param):
    cursor.movePosition(QTextCursor.Down, param['anchor'], 10)
    return cursor


def undo_cursor(self, cursor, _):
    if self.undo_cursor_position > 0:
        self.redo_cursor_position = cursor.position()
        cursor.setPosition(self.undo_cursor_position)
        center_cursor(self, cursor)

    return cursor


def redo_cursor(self, cursor, _):
    if self.redo_cursor_position > 0:
        cursor.setPosition(self.redo_cursor_position)
        center_cursor(self, cursor)

    return cursor


def goto_function(self, cursor, _):
    pos = cursor.position()
    self.undo_cursor_position = pos

    cursor.select(QTextCursor.WordUnderCursor)
    word = cursor.selectedText()
    cursor.clearSelection()
    cursor.setPosition(pos)

    code = self.toPlainText()
    def_line = None

    try:
        node_ast = ast.parse(code)
        for node in node_ast.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if not word == node.name:
                continue

            def_line = node.lineno
            break
    except:
        tb = str(traceback.format_exc())

        line_number = tb.rsplit('line', 1)[-1].strip().split(' ')[0]
        line_number = ''.join(
            [c if c.isdigit() else '' for c in line_number])

        line_number = int(line_number)
        print(tb)
        print(line_number)

        self.parent.set_line_error(line_number)
        return


    if def_line:
        block = self.document().findBlockByNumber(def_line - 1)
        cursor.setPosition(block.position())
        go_to_first_char(cursor)
        cursor.movePosition(QTextCursor.NextWord)
        center_cursor(self, cursor, None)
    else:
        print('Definition "{}" not found !'.format(word))

    return cursor
