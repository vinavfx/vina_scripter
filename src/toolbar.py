# -*- coding: utf-8 -*-
# -----------------------------------------------------------
# AUTHOR --------> Francisco Jose Contreras Cuevas
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------

from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QComboBox, QLabel
from PySide2.QtGui import QIcon

from ..nuke_util.nuke_util import get_nuke_path
icons_path = '{}/vina_scripter/icons'.format(get_nuke_path())


class toolbar_widget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        layout = QHBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)
        self.setLayout(layout)

        self.enter_node_button = QPushButton()
        self.enter_node_button.setIcon(
            QIcon('{}/icon_pick.png'.format(icons_path)))
        self.enter_node_button.setToolTip('Enter to Node')
        self.enter_node_button.clicked.connect(
            lambda: self.parent.enter_node())

        exec_script_button = QPushButton()
        exec_script_button.setIcon(
            QIcon('{}/icon_run.png'.format(icons_path)))
        exec_script_button.setToolTip('Execute current Knob')
        exec_script_button.clicked.connect(self.parent.execute_script)

        clean_output_button = QPushButton()
        clean_output_button.setIcon(
            QIcon('{}/clear_console.png'.format(icons_path)))
        clean_output_button.setToolTip('Clean output console')
        clean_output_button.clicked.connect(self.parent.clean_output_console)

        self.node_edit_widget = self.node_edit_buttons()

        buttons_layout = QHBoxLayout()
        buttons_layout.setMargin(0)
        buttons_layout.setSpacing(5)
        self.page_buttons_widget = QWidget()
        self.page_buttons_widget.setLayout(buttons_layout)

        self.vim_mode_button = QPushButton()
        self.vim_mode_button.setCheckable(True)
        self.vim_mode_button.setToolTip('Same functionality as the VIM editor')
        self.vim_mode_button.setIcon(
            QIcon('{}/vim.png'.format(icons_path)))
        self.vim_mode_button.toggled.connect(self.parent.set_vim_mode)

        layout.addWidget(self.enter_node_button)
        layout.addWidget(self.node_edit_widget)
        layout.addWidget(self.page_buttons_widget)
        layout.addStretch()
        layout.addWidget(exec_script_button)
        layout.addWidget(clean_output_button)
        layout.addWidget(self.vim_mode_button)

    def node_edit_mode(self, active):
        self.node_edit_widget.setVisible(active)
        self.page_buttons_widget.setVisible(not active)

    def node_edit_buttons(self):
        self.exit_node_button = QPushButton('')
        self.exit_node_button.setIcon(
            QIcon('{}/icon_exitnode.png'.format(icons_path)))
        self.exit_node_button.setToolTip('Exit from Node')
        self.exit_node_button.clicked.connect(self.parent.exit_node)

        self.restore_script_button = QPushButton()
        self.restore_script_button.setIcon(
            QIcon('{}/icon_download.png'.format(icons_path)))
        self.restore_script_button.setToolTip('Restore original Script')
        self.restore_script_button.clicked.connect(self.parent.restore)

        self.save_script_button = QPushButton()
        self.save_script_button.setIcon(
            QIcon('{}/icon_save.png'.format(icons_path)))
        self.save_script_button.setToolTip('Save Script to Node')
        self.save_script_button.clicked.connect(self.parent.save)

        self.knob_selector = QComboBox()
        self.knob_selector.currentTextChanged.connect(
            self.parent.knob_selector_changed)

        self.current_node_label = QLabel()

        layout = QHBoxLayout()
        layout.setMargin(0)
        widget = QWidget()
        widget.setLayout(layout)

        layout.addWidget(self.exit_node_button)
        layout.addWidget(self.current_node_label)
        layout.addWidget(self.knob_selector)
        layout.addWidget(self.restore_script_button)
        layout.addWidget(self.save_script_button)

        return widget

    def set_page(self, page):
        for button in self.page_buttons_widget.findChildren(QPushButton):
            name = button.objectName()
            if name == str(page):
                button.setChecked(True)
                continue

            button.setChecked(False)

    def clear_pages(self):
        layout = self.page_buttons_widget.layout()

        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            del child

    def add_page(self, page):
        icon = QIcon('{}/develop.png'.format(icons_path))

        self.page_button = QPushButton()
        self.page_button.setObjectName(str(page))
        self.page_button.clicked.connect(
            lambda: self.parent.set_script_page(page))
        self.page_button.setCheckable(True)
        self.page_button.setToolTip('Script Page Nº {}'.format(page + 1))
        self.page_button.setIcon(icon)

        self.page_buttons_widget.layout().addWidget(self.page_button)


    def set_knob_selector_text(self, text):
        self.knob_selector.currentTextChanged.disconnect()
        self.knob_selector.setCurrentText(text)
        self.knob_selector.currentTextChanged.connect(
            self.parent.knob_selector_changed)
