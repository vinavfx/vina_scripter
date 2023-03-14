# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
from PySide2.QtWidgets import QVBoxLayout

from ..nuke_util.panels import panel_widget, float_panel_widget

from .scripter import scripter_widget

class panel_scripter(panel_widget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setMargin(0)
        self.setLayout(layout)

        scripter = scripter_widget()
        layout.addWidget(scripter)


class float_scripter(float_panel_widget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        #  layout.setMargin(0)
        self.setLayout(layout)

        scripter = scripter_widget()
        layout.addWidget(scripter)

        self.setWindowTitle('Vina Scripter')
        self.resize(700, 700)
        self.center_window()


