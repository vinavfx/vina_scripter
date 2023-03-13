# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
from statistics import mode

from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QTextCursor
from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit


class vim_widget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        QWidget.__init__(self)

        layout = QHBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        self.mode_label = QLabel('NORMAL')
        self.command_line = QLineEdit()
        self.command_line.setFont(QFont(self.parent.fonts[2], 9))

        self.command_line.setToolTip('w : Save script to node\n'
                                     'wq : Save and Exit\n'
                                     'q : Exit node\n'
                                     'tabnew : New script page\n'
                                     'tabclose : Close script page\n'
                                     'tabo : Close all except the current page\n'
                                     '1, 2, 3... : Go to line\n'
                                     '/ : Search\n'
                                     '%s/src/dst/g : Search and replace\n'
                                     'retab : Change the indentation to 4 spaces'
                                     )

        layout.addWidget(self.mode_label)
        layout.addWidget(self.command_line)

        scripter = self.parent.parent

        self.commands = {
            'w': scripter.save,
            'q': scripter.exit_node,
            'wq': lambda: (scripter.save(), scripter.exit_node()),
            'tabnew': scripter.add_page,
            'tabclose': scripter.remove_current_page,
            'tabo': scripter.clean_all_pages,
            'retab': self.retab
        }

    def set_mode(self, mode):
        if mode == 'visual' or mode == 'visual_line':
            label_mode = '<b><font color=#c27ddb>{}</font></b>'.format(
                mode.replace('_', ' ').upper())
        elif mode == 'insert':
            label_mode = '<b><font color=#57c1de>{}</font></b>'.format(
                mode.upper())
        else:
            label_mode = '<b>{}</b>'.format(mode.upper())

        self.mode_label.setText(label_mode)

    def keyPressEvent(self, event):
        ctrl = event.modifiers() == Qt.ControlModifier
        key = event.key()

        if ctrl and key == Qt.Key_BracketLeft or key == Qt.Key_Escape:
            self.command_line.clear()
            self.parent.set_focus()
            return

        if (ctrl and key == Qt.Key_Return
            or ctrl and key == Qt.Key_M
            or key == Qt.Key_Return
            ):

            self.run_command()
            self.command_line.clear()
            self.parent.set_focus()
            return

        QWidget.keyPressEvent(self, event)

    def retab(self):
        editor = self.parent.editor

        def get_first_char_index(line_text):
            current = 0
            for c in line_text:
                if c.isspace():
                    current += 1
                    continue
                break

            return current

        def get_current_indent_count():
            indents = []

            for l in editor.toPlainText().splitlines():
                if l:
                    indents.append(get_first_char_index(l))

            diffs = []

            for i in range(len(indents)-1):
                diff = abs(indents[i] - indents[i+1])
                if diff:
                    diffs.append(diff)

            if not diffs:
                return 2

            try:
                return mode(diffs)
            except:
                return 4

        prev_indent = get_current_indent_count()

        cursor = editor.textCursor()
        pos = cursor.position()
        cursor.beginEditBlock()

        cursor.movePosition(QTextCursor.Start)

        for _ in range(editor.document().blockCount()):

            cursor.movePosition(QTextCursor.StartOfLine)
            text = cursor.block().text()

            current_indent = get_first_char_index(text)

            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

            spaces = current_indent
            if prev_indent == 2:
                spaces = 2 * current_indent
            elif prev_indent == 3:
                spaces = (current_indent + int(current_indent / 3))
            elif prev_indent == 6:
                spaces = (current_indent - int(current_indent / 3))
            elif prev_indent == 8:
                spaces = int(current_indent / 2)

            if not spaces % 4 == 0:
                spaces += 4 - spaces % 4

            spaces = spaces * ' '

            new_text = '{}{}'.format(spaces, text[current_indent:])
            cursor.removeSelectedText()
            cursor.insertText(new_text)

            cursor.movePosition(QTextCursor.Down)

        cursor.endEditBlock()
        cursor.setPosition(pos)
        editor.setTextCursor(cursor)

    def go_to_line(self, line):
        cursor = self.parent.editor.textCursor()

        line_count = self.parent.editor.document().lineCount()
        if line > line_count:
            line = line_count

        cursor.setPosition(self.parent.editor.document(
        ).findBlockByLineNumber(line - 1).position())
        self.parent.editor.setTextCursor(cursor)

    def run_command(self):
        command = self.command_line.text()[1:]

        prefix = self.command_line.text()[:1]

        if prefix == '/':
            self.parent.editors[0].editor.is_search = True
            self.parent.editors[0].editor.highlight_word(command)

        elif command.isdigit():
            self.go_to_line(int(command))

        elif not command in self.commands:
            print("'{}' command does not exist !".format(command))

        else:
            self.commands[command]()

    def write_command(self, prefix):
        self.command_line.setFocus()
        self.command_line.setText(prefix)
