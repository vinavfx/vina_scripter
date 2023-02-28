# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
from PySide2.QtWidgets import QTextEdit, QApplication, QSplitter
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QTextCursor


def get_nuke_script_editor():
    for widget in QApplication.allWidgets():
        if widget.metaObject().className() == 'Nuke::NukeScriptEditor':
            return widget


def get_nuke_console():
    se = get_nuke_script_editor()

    if not se:
        return

    children = se.children()
    splitter = [w for w in children if isinstance(w, QSplitter)]

    if not splitter:
        return

    splitter = splitter[0]
    for widget in splitter.children():
        if widget.metaObject().className() == 'Foundry::PythonUI::ScriptOutputWidget':
            return widget

    return None


class output_widget(QTextEdit):
    def __init__(self, parent):
        QTextEdit.__init__(self, parent)
        self.parent = parent
        self.setReadOnly(True)
        self.setFont(QFont(parent.fonts[2], 9))

        self.nuke_console = get_nuke_console()
        if not self.nuke_console:
            return

        self.nuke_console.textChanged.connect(self.update_output)
        self.setText(self.nuke_console.toPlainText())

    def update_output(self):
        if not self.nuke_console:
            return

        text1 = self.toPlainText()
        text2 = self.nuke_console.toPlainText()

        i = 0
        while i < len(text1) and i < len(text2) and text1[i] == text2[i]:
            i += 1

        new_text = self.nuke_console.toPlainText()[i:]

        text_cursor = self.textCursor()
        text_cursor.movePosition(QTextCursor.End)
        self.setTextCursor(text_cursor)

        self.insertPlainText(new_text)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear_all(self):
        if not self.nuke_console:
            return

        self.clear()
        self.nuke_console.clear()

    def add_output(self, output):
        if not self.nuke_console:
            return

        self.nuke_console.append(output)

    def keyPressEvent(self, event):
        ctrl = event.modifiers() == Qt.ControlModifier
        key = event.key()

        if ctrl and key == Qt.Key_Return:
            self.parent.execute_script()
        elif ctrl and key == Qt.Key_Backspace:
            self.parent.clean_output_console()
        elif key == Qt.Key_Escape:
            self.parent.exit_node()

        QTextEdit.keyPressEvent(self, event)
