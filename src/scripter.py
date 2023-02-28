# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
import traceback
import os
import sys
from random import randint

from PySide2.QtGui import QColor, QKeySequence
from PySide2.QtWidgets import QVBoxLayout, QShortcut, QSplitter
from PySide2.QtCore import Qt

import nuke

from .python_highlighter import KSPythonHighlighter
from .blink_highlighter import KSBlinkHighlighter
from .editor import editor_widget
from .script_output import output_widget
from .toolbar import toolbar_widget

from ..nuke_util.panels import panel_widget
from ..python_util.util import jread, jwrite
from ..nuke_util.nuke_util import get_nuke_path


class scripter_widget(panel_widget):
    def __init__(self, parent=None):
        panel_widget.__init__(self, parent)
        layout = QVBoxLayout()
        layout.setMargin(0)
        self.setLayout(layout)

        self.setWindowTitle('Knob Scripter')
        self.setWindowFlags(Qt.Tool)
        self.resize(700, 500)

        self.fonts = ['Consolas', 'Courier New', 'Inconsolata']

        ctrl_s_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        ctrl_s_shortcut.activatedAmbiguously.connect(self.save)

        self.editor = editor_widget(self)

        self.console = output_widget(self)
        self.toolbar = toolbar_widget(self)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.console)
        splitter.addWidget(self.editor)
        splitter.setSizes([splitter.height() * 0.35, splitter.height() * 0.65])

        layout.addWidget(self.toolbar)
        layout.addWidget(splitter)

        self.current_node = None
        self.current_node_name = ''
        self.current_node_obj_name = ''

        self.current_knob = None
        self.modified_knob = False

        self.python_syntax = True
        self.python_highlight = KSPythonHighlighter()
        self.blink_highlight = KSBlinkHighlighter()
        self.python_highlight.setDocument(self.editor.editor.document())

        self.last_knob_name = ''
        self.state = {
            'pages': [''],
            'current_page': 0,
            'vim_mode': True
        }

        self.exit_node()

        self.enter_node_menu = nuke.menu('Nuke').addCommand(
            'Edit/Node/Edit Script ( Knob Scripter )', self.enter_node, 'alt+z')

        nuke.menu('Animation').addCommand(
            'Python Expression', 'vina_scripter.vina_scripter.scripter.main_widget.edit_python_expression()')

        nuke.addOnDestroy(lambda: self.exit_node(True)
                          if nuke.thisNode() == self.current_node else None)

        nuke.addOnScriptClose(lambda: self.save_state(False))

        self.state_file = '{}/vina_scripter_state.json'.format(get_nuke_path())
        self.restored_state = False
        self.python_knobs_list = ['PythonKnob', 'PyScript_Knob', 'PythonCustomKnob']

    def showEvent(self, event):
        self.restore_state()
        return panel_widget.showEvent(self, event)

    def save_state(self, save_code=True):
        if save_code:
            self.set_script_page(self.state['current_page'])

        jwrite(self.state_file, self.state)

    def restore_state(self):
        if self.restored_state:
            return

        self.restored_state = True

        if os.path.isfile(self.state_file):
            self.state = jread(self.state_file)

        for page in range(len(self.state['pages'])):
            self.toolbar.add_page(page)

        self.set_script_page(self.state['current_page'], False)
        self.set_vim_mode(self.state['vim_mode'])

    def set_vim_mode(self, checked):
        if not self.toolbar.vim_mode_button.isChecked() == checked:
            self.toolbar.vim_mode_button.setChecked(checked)

        self.editor.set_vim_mode(checked)
        self.state['vim_mode'] = checked

    def set_script_page(self, page, save_previous=True):
        if self.current_node:
            return

        if save_previous:
            self.state['pages'][self.state['current_page']
                                ] = self.editor.get_code()

        self.toolbar.set_page(page)
        code = self.state['pages'][page]
        self.state['current_page'] = page

        cursor_name = 'script_{}'.format(page)
        self.set_code(code, cursor_name)

    def get_script_current_page(self):
        pages = self.state['pages']
        current_page = self.state['current_page']

        return pages[current_page]

    def add_page(self):
        page = len(self.state['pages'])

        if self.current_node:
            self.exit_node()

        if page == 10:
            nuke.message('Maximum 10 page, delete to have space !')
            return

        self.toolbar.add_page(page)
        self.state['pages'].append('')
        self.set_script_page(page)

    def remove_current_page(self):
        self.toolbar.clear_pages()

        current_page = self.state['current_page']
        del self.state['pages'][current_page]

        for page in range(len(self.state['pages'])):
            self.toolbar.add_page(page)

        new_current_page = current_page - 1 if current_page > 1 else 0

        self.state['current_page'] = new_current_page
        self.toolbar.set_page(new_current_page)

        code = self.state['pages'][new_current_page]
        self.set_code(code)

    def clean_all_pages(self):
        if not nuke.ask('Only the current page will be kept and all the others will be deleted, continue ?'):
            return

        current_page = self.state['current_page']
        code = self.state['pages'][current_page]

        self.toolbar.clear_pages()

        self.state['current_page'] = 0
        self.state['pages'] = [code]

        self.toolbar.add_page(0)
        self.toolbar.set_page(0)

    def next_script_page(self):
        page = self.state['current_page']

        if page >= len(self.state['pages']) - 1:
            page = 0
        else:
            page += 1

        self.set_script_page(page)

    def previous_script_page(self):
        page = self.state['current_page']

        if page <= 0:
            page = len(self.state['pages']) - 1
        else:
            page -= 1

        self.set_script_page(page)

    def edit_python_expression(self):
        self.enter(nuke.thisNode(), nuke.thisKnob())

    def get_py_knobs(self, node):
        python_knobs = []
        py_buttons = []
        py_expressions = []

        for _, knob in node.knobs().items():
            if knob.Class() == 'PythonKnob' or knob.Class() == 'PythonCustomKnob':
                python_knobs.append(knob)

            if knob.Class() == 'PyScript_Knob':
                py_buttons.append(knob)

            if self.is_python_expression(knob):
                py_expressions.append(knob)

        return py_buttons, python_knobs, py_expressions

    def is_python_expression(self, knob):
        return 'python -execlocal' in knob.toScript()

    def editor_changed(self):
        self.set_modified_knob(True)

    def get_python_expression(self, knob):
        if not self.is_python_expression(knob):
            return ''

        exp = knob.toScript().split('python -execlocal ')[-1][:-3]
        exp = exp.replace("\\n", "\n").replace("\\", "")

        return exp

    def get_blinkscript_source(self, knob):
        if not knob.name() == 'kernelSource':
            return ''

        return knob.toScript()

    def set_python_expression(self, knob, code):
        code = code.replace('\n', '\\n').replace(
            ']', '\\]').replace('[', '\\[').replace(' ', '\\ ')

        exp = '[python -execlocal {} ]'.format(code)

        knob.setExpression(exp)

        return True

    def knob_selector_changed(self, knob_name):
        if not self.current_node:
            return

        if not self.check_and_save() and self.current_knob:
            self.toolbar.set_knob_selector_text(self.current_knob.name())
            return

        self.current_knob = self.current_node.knob(knob_name)

        py_expression = self.get_python_expression(self.current_knob)
        blink_source = self.get_blinkscript_source(self.current_knob)

        if blink_source:
            code = blink_source
        elif py_expression:
            code = py_expression
        else:
            code = self.current_knob.value()

        cursor_name = self.current_node_name + self.current_knob.name()
        self.set_code(code, cursor_name, not blink_source)


    def enter_node(self):
        nodes = nuke.selectedNodes()

        if not nodes:
            nuke.message('Select only 1 node !')
            return
        if len(nodes) > 1:
            nuke.message('Select only 1 node !')
            return

        if not self.current_node:
            self.save_state()

        self.enter(nodes[0])

    def enter(self, node, knob_expression=None):
        if not self.exit_node():
            return

        self.current_node = node
        self.current_node_name = self.current_node.fullName()
        self.current_node_obj_name = str(self.current_node.__str__)

        node_name = 'Node: <b>{}</b>'.format(self.current_node.name())
        self.toolbar.current_node_label.setText(node_name)

        py_buttons, python_knobs, py_expressions = self.get_py_knobs(
            self.current_node)

        if knob_expression:
            if not self.is_python_expression(knob_expression):
                knob_expression.setExpression('[python -execlocal ret = 0]')
            self.toolbar.knob_selector.addItem(knob_expression.name())

        for knob in py_expressions:
            if knob == knob_expression:
                continue
            self.toolbar.knob_selector.addItem(knob.name())

        for knob in py_buttons:
            self.toolbar.knob_selector.addItem(knob.name())

        for knob in python_knobs:
            self.toolbar.knob_selector.addItem(knob.name())

        if knob_expression:
            self.toolbar.knob_selector.setCurrentText(knob_expression.name())
        else:
            self.toolbar.knob_selector.setCurrentText(self.last_knob_name)

        self.set_modified_knob(False)

        self.toolbar.node_edit_mode(True)
        self.editor.editor.setFocus()

    def set_modified_knob(self, modified):
        if self.modified_knob == modified:
            return

        if not self.current_node:
            return

        self.modified_knob = modified

        save_script_button = self.toolbar.save_script_button

        def set_color(widget, color):
            p = widget.palette()
            p.setColor(widget.backgroundRole(), color)
            widget.setPalette(p)

        if modified:
            set_color(save_script_button, QColor(110, 60, 50))
        else:
            set_color(save_script_button, QColor(75, 75, 75))

    def set_code(self, code, cursor_name='', python_syntax=True):
        if not python_syntax == self.python_syntax:
            self.python_syntax = python_syntax
            document = self.editor.editor.document()

            if python_syntax:
                self.python_highlight.setDocument(document)
            else:
                self.blink_highlight.setDocument(document)

        self.editor.set_code(code, cursor_name)

    def restore(self):
        if not self.current_knob:
            return

        if not self.modified_knob:
            return

        if not nuke.ask('The new code will be deleted, continue ?'):
            return

        cursor_name = self.current_node_name + self.current_knob.name()

        if self.current_knob.Class() in self.python_knobs_list:
            if self.current_knob.name() == 'kernelSource':
                self.set_code(self.current_knob.toScript(), cursor_name, False)
            else:
                self.set_code(self.current_knob.value(), cursor_name)
        else:
            self.set_code(self.get_python_expression(self.current_knob), cursor_name)

        self.set_modified_knob(False)

    def save(self):
        if not self.current_knob or not self.current_node:
            self.save_state()
            return

        code = self.editor.get_code()

        if self.current_knob.Class() in self.python_knobs_list:
            if self.current_knob.name() == 'kernelSource':
                self.current_knob.fromScript(code)
                self.current_node.knob('recompile').execute()
            else:
                self.current_knob.setValue(code)
        else:
            self.set_python_expression(self.current_knob, code)

        self.set_modified_knob(False)

    def check_and_save(self):
        if not self.modified_knob:
            return True

        if not self.current_node:
            return False

        try:
            if nuke.askWithCancel('The knob was modified, you want to save before exiting ?'):
                self.save()
        except:
            return False

        self.set_modified_knob(False)
        return True

    def exit_node(self, force = False):
        if not force:
            if not self.check_and_save():
                return False

        self.set_modified_knob(False)

        if self.current_knob:
            self.last_knob_name = self.current_knob.name()

        self.current_knob = None
        self.current_node = None
        self.current_node_name = ''
        self.current_node_obj_name = ''

        self.toolbar.node_edit_mode(False)

        self.toolbar.knob_selector.clear()

        cursor_name = 'script_{}'.format(self.state['current_page'])
        self.set_code(self.get_script_current_page(), cursor_name)

        return True

    def clean_output_console(self):
        self.console.clear_all()

    def execute_script(self):
        code = self.editor.get_code()

        if not code.strip():
            return

        if not self.python_syntax and self.current_node:
            self.save()
            return

        run_context = 'root'

        if self.current_node and self.current_knob:
            run_context = "{}.{}".format(
                self.current_node_name, self.current_knob.name())
        else:
            self.save_state()

        code = "exec('''{}''')".format(
            code.replace("\\", "\\\\").replace("'", "\\'"))

        print('# Result: ')

        try:
            nuke.runIn(run_context, code)
        except:
            tb = str(traceback.format_exc())
            self.console.add_output(tb)

            line_number = tb.rsplit('line', 1)[-1].strip().split(' ')[0]
            line_number = ''.join(
                [c if c.isdigit() else '' for c in line_number])

            line_number = int(line_number)
            self.editor.set_line_error(line_number)
