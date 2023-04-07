# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
import traceback
import os
import re

from PySide2.QtGui import QColor, QKeySequence
from PySide2.QtWidgets import QVBoxLayout, QShortcut, QSplitter, QApplication, QTextEdit, QWidget
from PySide2.QtCore import Qt

import nuke

from .editor import multi_editor_widget
from .script_output import output_widget
from .toolbar import toolbar_widget

from ..python_util.util import jread, jwrite
from ..nuke_util.nuke_util import get_nuke_path


class scripter_widget(QWidget):
    def __init__(self, parent, float_panel=False):
        super(scripter_widget, self).__init__()
        self.float_panel = float_panel
        self.parent = parent

        layout = QVBoxLayout()
        layout.setMargin(0)
        self.setLayout(layout)

        self.setWindowTitle('Knob Scripter')
        self.setWindowFlags(Qt.Tool)
        self.resize(700, 500)

        self.fonts = ['Consolas', 'Courier New', 'Inconsolata']

        ctrl_s_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        ctrl_s_shortcut.activatedAmbiguously.connect(self.save)

        self.editor = multi_editor_widget(self)

        self.console = output_widget(self)
        self.toolbar = toolbar_widget(self)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.console)
        splitter.addWidget(self.editor)
        splitter.setSizes([splitter.height() * 0.25, splitter.height() * 0.75])

        layout.addWidget(self.toolbar)
        layout.addWidget(splitter)

        self.current_node = None
        self.current_node_name = ''
        self.current_node_obj_name = ''

        self.current_knob = None
        self.modified_knob = False
        self.tcl_errors = {}

        self.activated_knob_changed = True

        self.last_knob_name = ''
        self.state = {
            'pages': [''],
            'current_page': 0,
            'vim_mode': True
        }

        self.exit_node()

        nuke.addOnDestroy(lambda: self.exit_node(True)
                          if nuke.thisNode() == self.current_node else None)

        nuke.addKnobChanged(self.knob_changed)

        nuke.addOnScriptClose(lambda: self.save_state(False))

        self.state_file = '{}/vina_scripter_state.json'.format(get_nuke_path())
        self.restored_state = False
        self.python_knobs_list = ['PythonKnob',
                                  'PyScript_Knob', 'PythonCustomKnob']

    def showEvent(self, event):
        self.restore_state()
        super(scripter_widget, self).showEvent(event)

    def save_state(self, save_code=True):
        if save_code:
            self.set_script_page(self.state['current_page'])

        jwrite(self.state_file, self.state)

    def knob_changed(self):
        if not self.current_knob == nuke.thisKnob():
            return

        if not self.current_knob:
            return

        if not self.activated_knob_changed:
            return

        node = self.current_node
        self.exit_node()
        self.enter(node)

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

    def edit_expression(self, tcl=False):
        knob = nuke.thisKnob()

        dimension = self.thisDimension()
        is_tcl = self.is_tcl_expression(knob, dimension)

        if not is_tcl == tcl and knob.hasExpression(dimension):
            msg = 'A {} expression already exists, do you want to replace it with {}?'.format(
                'tcl' if is_tcl else 'python',
                'python' if is_tcl else 'tcl')

            if nuke.ask(msg):
                knob.clearAnimated(dimension)

        syntax = 'tcl' if tcl else 'python'
        self.enter(nuke.thisNode(), knob, syntax, dimension)

    def get_py_knobs(self, node):
        python_knobs = []
        py_buttons = []
        expressions = []

        for _, knob in node.knobs().items():
            if knob.Class() == 'PythonKnob' or knob.Class() == 'PythonCustomKnob':
                python_knobs.append(knob)

            elif knob.Class() == 'PyScript_Knob':
                py_buttons.append(knob)

            elif knob.hasExpression():
                expressions.append(knob)


        return py_buttons, python_knobs, expressions

    def is_tcl_expression(self, knob, dimension=0):
        if not knob.hasExpression():
            return False

        if self.is_python_expression(knob, dimension):
            return False

        return True

    def editor_changed(self):
        self.set_modified_knob(True)


    def get_raw_expression(self, knob):
        raw_exprs = [None, None, None, None]
        anim_index = 0

        for d in range(knob.arraySize()):
            if knob.hasExpression(d):
                raw_exprs[d] = knob.animations()[anim_index].expression()
                anim_index += 1

        return raw_exprs

    def get_expression(self, knob):

        exprs = [None, None, None, None]
        if not hasattr(knob, 'singleValue'):
            return exprs

        raw_exprs = self.get_raw_expression(knob)

        def append_expr(dimension):
            expr = raw_exprs[dimension]

            if expr == None:
                return

            if self.is_tcl_expression(knob, dimension):
                if any(i in expr for i in ['return', 'set ']):
                    expr = expr.split('[', 1)[1].rsplit(']', 1)[0]

                exprs[dimension] = {'value': expr, 'syntax': 'tcl'}

            else:
                if '-execlocal' in expr:
                    expr = expr.split('python -execlocal ')[-1][:-1]
                else:
                    expr = expr.split('python ')[-1][:-1]

                expr = expr.replace("\\n", "\n").replace("\\", "")

                exprs[dimension] = {'value': expr, 'syntax': 'python'}

        if knob.singleValue():
            append_expr(0)
        else:
            for d in range(4):
                append_expr(d)

        return exprs

    def get_blinkscript_source(self, knob):
        if not knob.name() == 'kernelSource':
            return ''

        return knob.toScript()

    def line_count(self, code):
        lines = code.split('\n')
        lines = [line for line in lines if line.strip()]

        return len(lines)

    def is_python_expression(self, knob, dimension=0):
        if not knob.hasExpression():
            return False

        dimension = dimension if dimension >= 0 else 0
        expr = self.get_raw_expression(knob)[dimension]

        if not expr:
            return False

        match = re.search(r'\b(?![^\w]+)\w+\b', expr)
        if not match:
            return False

        python_word = match.group()

        if python_word == 'python':
            return True

        return False

    def set_expression(self, knob, code, syntax='python', dimension=-1):
        if syntax == 'python':
            if self.line_count(code) > 1 or 'ret=' in code or 'ret ' in code:
                code = code.replace('\n', '\\n').replace(
                    ']', '\\]').replace('[', '\\[').replace(' ', '\\ ')

                exp = '[python -execlocal {} ]'.format(code)

            else:
                exp = '[python {}]'.format(code.replace('\n', '').strip())

        else:
            if any(w in code for w in ['return', 'set', 'expr']):
                exp = '[' + code + ']'
            else:
                exp = code

        self.activated_knob_changed = False
        knob.setExpression(exp, dimension)
        self.activated_knob_changed = True


    def knob_selector_changed(self, knob_name):
        if not self.current_node:
            return

        if not self.check_and_save() and self.current_knob:
            self.toolbar.set_knob_selector_text(self.current_knob.name())
            return

        self.current_knob = self.current_node.knob(knob_name)

        expression = self.get_expression(self.current_knob)
        blink_source = self.get_blinkscript_source(self.current_knob)

        codes = [None, None, None, None]

        if blink_source:
            codes[0] = {'value': blink_source, 'syntax': 'blink'}

        elif any(not d == None for d in expression):
            codes = expression

        else:
            codes[0] = {'value': str( self.current_knob.value() ), 'syntax': 'python'}

        cursor_name = self.current_node_name + self.current_knob.name()

        dimensions = [not d == None for d in codes]
        self.editor.set_dimensions(*dimensions)

        for d, code in enumerate(codes):
            if not code:
                continue

            value = code['value']
            syntax = code['syntax']
            self.editor.set_code(value, cursor_name, syntax, d)

    def enter_node(self):
        nodes = nuke.selectedNodes()

        if not nodes:
            nuke.message('Select only 1 node !')
            return False
        if len(nodes) > 1:
            nuke.message('Select only 1 node !')
            return False

        if not self.current_node:
            self.save_state()

        self.enter(nodes[0])
        return True

    def thisDimension(self):
        focus_widget = QApplication.focusWidget()
        focus_name = focus_widget.metaObject().className()

        if focus_name == 'NodePanel':
            return -1

        dimension = 0

        parent = focus_widget.parent()

        for child_widget in parent.children():
            child_name = child_widget.metaObject().className()

            if not focus_name == child_name:
                continue

            if child_widget == focus_widget:
                break

            dimension += 1

        return dimension

    def enter(self, node, knob_expression=None, expr_syntax='python', dimension=-1):
        if not self.exit_node(False, True):
            return

        self.current_node = node
        self.current_node_name = self.current_node.fullName()
        self.current_node_obj_name = str(self.current_node.__str__)

        node_name = 'Node: <b>{}</b>'.format(self.current_node.name())
        self.toolbar.current_node_label.setText(node_name)

        py_buttons, python_knobs, expressions_knobs = self.get_py_knobs(
            self.current_node)

        if knob_expression:
            if not knob_expression.hasExpression(dimension):
                if type(knob_expression) == nuke.Boolean_Knob:
                    default_value = knob_expression.value()
                else:
                    default_value = knob_expression.value(
                        dimension if dimension >= 0 else 0)

                self.set_expression(knob_expression, str(
                    default_value), expr_syntax, dimension)

            self.toolbar.knob_selector.addItem(knob_expression.name())

        for knob in expressions_knobs:
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
        self.editor.set_focus()

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

    def set_code(self, code, cursor_name='', syntax='python'):
        self.editor.set_code(code, cursor_name, syntax)

    def restore(self):
        if not self.current_knob:
            return

        if not self.modified_knob:
            return

        if not nuke.ask('The new code will be deleted, continue ?'):
            return

        node = self.current_node
        knob = self.current_knob

        self.exit_node(True)
        self.enter(node, knob)

    def save(self):
        self.activated_knob_changed = False
        knob = self.current_knob

        if not knob or not self.current_node:
            self.save_state()
            self.activated_knob_changed = True
            return

        if knob.Class() in self.python_knobs_list:
            code = self.editor.get_code(0)

            if knob.name() == 'kernelSource':
                knob.fromScript(code)
                self.current_node.knob('recompile').execute()
            else:
                knob.setValue(code)
        else:
            if knob.singleValue():
                code = self.editor.get_code(0)
                syntax = self.editor.get_syntax(0)
                self.set_expression(self.current_knob, code, syntax)

            else:
                for d in range(knob.arraySize()):
                    if not knob.hasExpression(d):
                        continue

                    code = self.editor.get_code(d)
                    syntax = self.editor.get_syntax(d)
                    self.set_expression(self.current_knob, code, syntax, d)

        self.set_modified_knob(False)
        self.activated_knob_changed = True

    def check_and_save(self):
        if not self.modified_knob:
            return True

        if not self.current_node:
            return False

        try:
            ask = nuke.ask if self.float_panel else nuke.askWithCancel
            if ask('The knob was modified, you want to save before exiting ?'):
                self.save()
        except:
            return False

        self.set_modified_knob(False)
        return True

    def exit_node(self, force=False, from_enter_node=False):
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

        self.tcl_errors.clear()

        self.toolbar.node_edit_mode(False)

        self.toolbar.knob_selector.clear()

        cursor_name = 'script_{}'.format(self.state['current_page'])
        self.set_code(self.get_script_current_page(), cursor_name)

        self.editor.set_dimensions()
        if not from_enter_node:
            self.editor.set_focus(0)

        return True

    def clean_output_console(self):
        self.console.clear_all()

    def get_nuke_error_console(self):
        def get_all_widgets(widget):
            widgets = [widget]
            for child in widget.findChildren(QTextEdit):
                widgets += get_all_widgets(child)

            return widgets

        for widget in get_all_widgets(QApplication.activeWindow()):
            if not widget.metaObject().className() == 'ErrorOutput':
                continue

            return widget

        return None

    def execute_tcl(self, code, dimension):
        knob = self.current_knob
        if not knob:
            return

        expr = self.get_expression(knob)[dimension]
        if not expr:
            return

        aux = expr['value']

        code = self.editor.get_code(dimension)
        self.set_expression(knob, code, 'tcl', dimension)

        if type(knob) == nuke.Boolean_Knob:
            result = knob.value()
        else:
            result = knob.value(dimension)

        error_console = self.get_nuke_error_console()
        error = error_console.toPlainText().strip() if error_console else ''

        key = re.sub('\\s+', ' ', code)

        if error_console and error:
            err = error.splitlines()[-1].split(':', 2)[-1]
            err = 'ERROR:{}'.format(err)
            print(err)
            self.tcl_errors[key] = err
            error_console.clear()

        elif key in self.tcl_errors:
            print(self.tcl_errors[key])

        else:
            print(result)

        self.set_expression(knob, aux, 'tcl', dimension)


    def execute_python(self, code):
        run_context = 'root'

        if self.current_node and self.current_knob:
            run_context = "{}.{}".format(
                self.current_node_name, self.current_knob.name())
        else:
            self.save_state()

        python_code = "exec('''{}''')".format(
            code.replace("\\", "\\\\").replace("'", "\\'"))

        try:
            nuke.runIn(run_context, python_code)
        except:
            tb = str(traceback.format_exc())
            self.console.add_output(tb)

            line_number = tb.rsplit('line', 1)[-1].strip().split(' ')[0]
            line_number = ''.join(
                [c if c.isdigit() else '' for c in line_number])

            line_number = int(line_number)
            self.editor.set_line_error(line_number)

    def execute_script(self):
        dimension = self.editor.get_focus_dimension()
        code = self.editor.get_code(dimension)

        if not code.strip():
            return

        syntax = self.editor.get_syntax(dimension)

        if syntax == 'blink' and self.current_node:
            self.save()

        elif syntax == 'python':
            self.execute_python(code)

        else:
            self.execute_tcl(code, dimension)
