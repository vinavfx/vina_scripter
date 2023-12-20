# -----------------------------------------------------------
# AUTHOR --------> Francisco Jose Contreras Cuevas
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtCore import Qt

from ..nuke_util.panels import panel_widget, float_panel_widget

from .scripter import scripter_widget

class panel_scripter(panel_widget):
    def __init__(self, parent=None):
        super(panel_scripter, self).__init__(parent)
        self.margin = 2

        layout = QVBoxLayout()
        layout.setMargin(0)
        self.setLayout(layout)

        self.scripter = scripter_widget(self)
        layout.addWidget(self.scripter)


class float_scripter(float_panel_widget):
    def __init__(self):
        self.scripter = None
        super(float_scripter, self).__init__()

        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.scripter = scripter_widget(self, float_panel=True)
        layout.addWidget(self.scripter)

        self.setWindowTitle('Vina Scripter')
        self.resize(700, 700)
        self.center_window()

    def closeEvent(self, event):
        if self.scripter:
            self.scripter.exit_node()

        return super(float_scripter, self).closeEvent(event)


