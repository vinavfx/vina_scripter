# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
import nuke

from PySide2.QtGui import QFont, QTextOption, QColor, QPainter, QTextFormat, QPalette, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit, QWidget, QTextEdit, QWidget, QVBoxLayout, QSplitter
from PySide2.QtCore import Qt, QRect, QRegExp

from .keys_normal_mode import key_press_event as normal_key_press_event
from .vim import keys_vim_mode
from .vim.vim import vim_widget
from .vim.vim_nav_actions import center_cursor

from .python_highlighter import KSPythonHighlighter
from .blink_highlighter import KSBlinkHighlighter
from .tcl_highlighter import tcl_highlighter

class multi_editor_widget(QWidget):
    def __init__(self, parent):
        super(multi_editor_widget, self).__init__()
        self.parent = parent

        layout = QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.fonts = ['Consolas', 'Courier New', 'Inconsolata']

        self.vim_mode = False
        self.vim = vim_widget(self)

        splitter = QSplitter(Qt.Vertical)

        self.editors = []
        for i in range(4):
            editor = editor_widget(self, i)
            editor.hide()
            splitter.addWidget(editor)
            self.editors.append(editor)

        layout.addWidget(splitter)
        layout.addWidget(self.vim)

        self.focus_dimension = 0
        self.set_dimensions()

    def set_dimensions(self, d1=True, d2=False, d3=False, d4=False):

        self.editors[0].setVisible(d1)
        self.editors[1].setVisible(d2)
        self.editors[2].setVisible(d3)
        self.editors[3].setVisible(d4)

    def goto_upper_code(self):
        dimension = self.focus_dimension - 1

        for _ in range(4):
            if dimension < 0:
                return

            if self.editors[dimension].isVisible():
                self.set_focus(dimension)
                return

            dimension -= 1

    def goto_lower_code(self):
        dimension = self.focus_dimension + 1

        for _ in range(4):
            if dimension > 3:
                return

            if self.editors[dimension].isVisible():
                self.set_focus(dimension)
                return

            dimension += 1

    def set_code(self, code, cursor_name='', syntax='python', dimension=0):
        self.editors[dimension].set_code(code, cursor_name, syntax)

    def set_vim_mode(self, vim_mode):
        self.vim_mode = vim_mode
        self.vim.setVisible(vim_mode)

        for editor in self.editors:
            editor.set_vim_mode(vim_mode)

    def get_focus_dimension(self):
        return self.focus_dimension

    def get_editor(self):
        return self.editors[self.focus_dimension].editor

    def get_code(self, dimension=0):
        return self.editors[dimension].get_code()

    def set_focus(self, dimension=-1):
        if dimension == -1:
            dimension = self.focus_dimension

        self.editors[dimension].editor.setFocus()

    def get_syntax(self, dimension=0):
        return self.editors[dimension].get_syntax()

    def set_line_error(self, line_number, dimension=0):
        self.editors[dimension].set_line_error(line_number)


class editor_widget(QWidget):
    def __init__(self, parent, index=0):
        QWidget.__init__(self)
        self.parent = parent
        self.index = index

        layout = QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.editor = code_editor(self)

        self.python_highlight = KSPythonHighlighter()
        self.blink_highlight = KSBlinkHighlighter()
        self.tcl_highlight = tcl_highlighter()

        self.syntax = 'python'
        self.python_highlight.setDocument(self.editor.document())

        layout.addWidget(self.editor)

        self.cursors_pile = {}
        self.current_cursor = ''

        self.text_changed_connected = False
        self.connect_changed()

    def connect_changed(self, connect=True):
        if self.text_changed_connected == connect:
            return

        self.text_changed_connected = connect

        if connect:
            self.editor.textChanged.connect(self.parent.parent.editor_changed)
        else:
            self.editor.textChanged.disconnect()

    def set_code(self, code, cursor_name='', syntax='python'):
        if self.current_cursor:
            self.cursors_pile[self.current_cursor] = self.editor.textCursor(
            ).position()

        if not code == self.get_code():
            self.connect_changed(False)
            self.editor.setPlainText(code)
            self.set_syntax(syntax)

        if not cursor_name == self.current_cursor and cursor_name in self.cursors_pile:
            pos = self.cursors_pile[cursor_name]
            cursor = self.editor.textCursor()
            cursor.setPosition(pos)
            self.editor.setTextCursor(cursor)

        self.current_cursor = cursor_name

        self.cursors_pile = {key: value for key,
                             value in self.cursors_pile.items() if value != 0}

    def set_syntax(self, syntax):
        if syntax == self.syntax:
            return

        self.syntax = syntax
        document = self.editor.document()

        self.python_highlight.setDocument(None)
        self.tcl_highlight.setDocument(None)
        self.blink_highlight.setDocument(None)

        if syntax == 'python':
            self.python_highlight.setDocument(document)

        elif syntax == 'tcl':
            self.tcl_highlight.setDocument(document)

        else:
            self.blink_highlight.setDocument(document)

    def get_syntax(self):
        return self.syntax

    def get_code(self):
        return self.editor.toPlainText()

    def set_line_error(self, line_number):
        self.editor.set_line_error(line_number)

    def set_vim_mode(self, vim_mode):
        self.editor.number_area.set_vim_mode(vim_mode)

        textOption = QTextOption()
        textOption.setWrapMode(
            QTextOption.NoWrap if vim_mode else QTextOption.WordWrap)

        self.editor.document().setDefaultTextOption(textOption)
        self.editor.setFocus()


class code_editor(QPlainTextEdit):
    def __init__(self, parent):
        super(code_editor, self).__init__()
        self.parent = parent

        keys_vim_mode.init(self)

        self.font_size = 10
        self.setFont(QFont(parent.parent.fonts[2], self.font_size))

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAcceptDrops(False)

        self.tab_spaces = 4
        self.tab_string = self.tab_spaces * ' '

        self.number_area = line_number_area(self)

        self.current_line_color = QColor(53, 53, 53)
        self.number_area_width = 30

        palette = self.palette()
        palette.setBrush(QPalette.Base, QColor(45, 45, 45))
        self.setPalette(palette)

        self.error_line = False
        self.set_mode('normal')

        self.cursorPositionChanged.connect(
            lambda: (self.number_area.update(), self.highlight_current_line()))

        self.blockCountChanged.connect(self.number_area.update)

        self.setViewportMargins(self.number_area_width + 2, 0, 0, 0)

        self.highlight_line_selection = None
        self.highlight_word_selections = []
        self.current_word = ''
        self.is_search = False

        self.backup_nuke_shortcut = []

    def focusInEvent(self, event):
        self.parent.parent.focus_dimension = self.parent.index
        self.disable_nuke_shortcut()
        super(code_editor, self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.disable_nuke_shortcut(False)
        super(code_editor, self).focusInEvent(event)

    def disable_nuke_shortcut(self, disable=True):
        if disable:
            nuke_actions = [
                nuke.menu('Nuke').menu('File').menu('Close Comp'),
                nuke.menu('Nuke').menu('File').menu('Open Comp...'),
                nuke.menu('Nuke').menu('Viewer').menu('Toggle Monitor Out'),
                nuke.menu('Nuke').menu('Viewer').menu('New Comp Viewer')
            ]

            self.backup_nuke_shortcut = []

            for act in nuke_actions:
                if not act:
                    continue

                self.backup_nuke_shortcut.append([act, act.shortcut()])
                act.setShortcut('')
        else:
            for act, shortcut in self.backup_nuke_shortcut:
                act.setShortcut(shortcut)

    def scrollContentsBy(self, dx, dy):
        self.number_area.update()
        super(code_editor, self).scrollContentsBy(dx, dy)

    def keyPressEvent(self, event):
        self.parent.connect_changed()

        ctrl = event.modifiers() == Qt.ControlModifier
        key = event.key()

        if key == Qt.Key_Escape:
            super(code_editor, self).keyPressEvent(event)

        if ctrl and (key == Qt.Key_M or key == Qt.Key_Return):
            self.parent.parent.parent.execute_script()
            return

        elif ctrl and key == Qt.Key_Backspace:
            self.parent.parent.parent.clean_output_console()
            return

        elif self.parent.parent.vim_mode:
            return keys_vim_mode.key_press_event(self, event)

        else:
            return normal_key_press_event(self, event)

    def resizeEvent(self, e):
        super(code_editor, self).resizeEvent(e)
        cr = self.contentsRect()
        rect = QRect(cr.left(), cr.top(), self.number_area_width, cr.height())
        self.number_area.setGeometry(rect)

    def set_mode(self, mode):
        self.parent.parent.vim.set_mode(mode)
        self.mode = mode

        if mode == 'normal':
            self.number_area.set_color(QColor(255, 200, 100))
        elif mode == 'insert':
            self.number_area.set_color(QColor(130, 220, 255))
        else:
            self.number_area.set_color(QColor(200, 100, 255))


    def set_line_error(self, line_number):

        textOption = QTextOption()
        textOption.setWrapMode(QTextOption.NoWrap)
        self.document().setDefaultTextOption(textOption)

        cursor = self.textCursor()
        pos = cursor.position()

        cursor.movePosition(cursor.Start)
        cursor.movePosition(cursor.Down, cursor.MoveAnchor, line_number - 1)
        self.setTextCursor(cursor)

        textOption = QTextOption()
        textOption.setWrapMode(
            QTextOption.NoWrap if self.parent.parent.vim_mode else QTextOption.WordWrap)
        self.document().setDefaultTextOption(textOption)

        cursor = center_cursor(self, cursor)
        cursor.setPosition(pos)
        self.setTextCursor(cursor)

        self.error_line = True
        self.highlight_current_line()


    def highlight_current_line(self):
        selection = QTextEdit.ExtraSelection()

        if self.error_line:
            selection.format.setBackground(QColor(80, 40, 50))
            self.error_line = False
        else:
            selection.format.setBackground(self.current_line_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)

        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()

        self.highlight_line_selection = selection

        extra_selections = [self.highlight_line_selection]
        extra_selections.extend(self.highlight_word_selections)

        self.setExtraSelections(extra_selections)

    def get_words(self, word=None):
        if not self.current_word:
            return []

        if not word:
            word = self.current_word

        pattern = r'\b{}\b'.format(word)
        if self.is_search:
            pattern = word

        regex = QRegExp(pattern)
        word_positions = []
        cursor = QTextCursor(self.document())

        while not cursor.isNull() and not cursor.atEnd():
            cursor = self.document().find(regex, cursor)
            if not cursor.isNull():
                word_positions.append(cursor.position()-len(word))
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)

        return word_positions

    def highlight_word_clean(self):
        self.highlight_word_selections = []
        extra_selections = [self.highlight_line_selection]

        if not any(extra_selections):
            return

        self.setExtraSelections(extra_selections)

    def highlight_word(self, word=None, cursor=None):
        if not word:
            word = self.current_word

        self.highlight_word_selections = []
        self.current_word = word

        words = self.get_words(word)

        if not cursor:
            cursor = self.textCursor()

        for pos in words:
            selection = QTextEdit.ExtraSelection()

            if pos == cursor.position():
                selection.format.setBackground(QColor(230, 190, 130))
            else:
                selection.format.setBackground(QColor(130, 190, 230))

            selection.format.setForeground(QColor(0, 0, 0))
            selection.cursor = cursor
            selection.cursor.clearSelection()
            selection.cursor.setPosition(pos)
            selection.cursor.movePosition(
                QTextCursor.Right, QTextCursor.KeepAnchor, len(word))

            self.highlight_word_selections.append(selection)

        extra_selections = [self.highlight_line_selection]
        extra_selections.extend(self.highlight_word_selections)

        if not any(extra_selections):
            return

        self.setExtraSelections(extra_selections)


class line_number_area(QWidget):
    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self.editor = editor

        self.background_color = QColor(50, 50, 50)
        self.text_color = QColor(170, 170, 170)
        self.current_text_color = QColor(255, 200, 100)

        self.vim_mode = False

    def set_vim_mode(self, vim_mode):
        self.vim_mode = vim_mode
        self.update()

    def set_color(self, color):
        self.current_text_color = color
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.fillRect(event.rect(), self.background_color)

        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()

        offset = self.editor.contentOffset()

        top = self.editor.blockBoundingGeometry(block).translated(offset).top()
        bottom = top + self.editor.blockBoundingRect(block).height()

        current_number = self.editor.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():

                number = str(block_number + 1)

                if current_number == block_number:
                    color = self.current_text_color
                else:
                    color = self.text_color
                    if self.vim_mode:
                        number = str(abs(current_number - block_number))

                painter.setPen(color)

                width = self.width()
                height = self.editor.fontMetrics().height()

                painter.drawText(-5, top, width, height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1

        painter.end()
