# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
from ..nuke_util.pyside import (
    Qt,
    QTimer,
    QFont,
    QTextEdit,
    QApplication,
    QSplitter,
)

nuke_console = None


def get_nuke_script_editor():
    for widget in QApplication.allWidgets():
        if widget.metaObject().className() == 'Nuke::NukeScriptEditor':
            return widget


def get_nuke_console():
    global nuke_console

    if nuke_console:
        return nuke_console

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
            nuke_console = widget
            return widget

    return None


class output_widget(QTextEdit):
    MAX_LINES = 1000

    def __init__(self, parent):
        QTextEdit.__init__(self, parent)
        self.parent = parent
        self.setReadOnly(True)
        self.setFont(QFont(parent.fonts[2], 9))
        self.last_pos = 0
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.flush)

    def flush(self):
        nuke_console = get_nuke_console()
        if nuke_console:
            lines = nuke_console.toPlainText().split('\n')
            self.setPlainText('\n'.join(lines[-self.MAX_LINES:]))
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def update_output(self):
        nuke_console = get_nuke_console()
        if not nuke_console:
            return

        text = nuke_console.toPlainText()
        if len(text) > self.last_pos:
            self.last_pos = len(text)
            if not self.timer.isActive():
                self.timer.start()

    def clear_all(self):
        nuke_console = get_nuke_console()
        if not nuke_console:
            return

        self.clear()
        nuke_console.clear()
        self.last_pos = 0

    def add_output(self, output):
        nuke_console = get_nuke_console()
        if not nuke_console:
            return

        nuke_console.append(output)

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
