# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import nuke
from . import src as vina_scripter
from .nuke_util import panels

from .src.script_output import get_nuke_console


nuke_console = None
nuke_console_connected = False


def setup():
    panels.init(
        'vina_scripter.vina_scripter.scripter_panel.panel_scripter', 'Vina Scripter')

    panels.init_float_panel(
        vina_scripter.scripter_panel.float_scripter, 'vina_scripter')

    nuke.menu('Nuke').addCommand(
        'Edit/Node/Edit Script ( Vina Scripter )', enter_node, 'alt+z')

    nuke.menu('Animation').addCommand(
        'Python Expression', 'vina_scripter.edit_expression()')

    nuke.menu('Animation').addCommand(
        'Tcl Expression', 'vina_scripter.edit_expression(True)')

    nuke.addUpdateUI(connect_to_nuke_console)


def connect_to_nuke_console(connect=True):
    global nuke_console, nuke_console_connected

    if nuke_console_connected == connect:
        return

    if not nuke_console:
        nuke_console = get_nuke_console()

    if not nuke_console:
        return

    if connect:
        nuke_console.textChanged.connect(update_consoles)
    else:
        nuke_console.textChanged.disconnect()

    nuke_console_connected = connect


def update_consoles():
    panel_widget = nuke.panels['vina_scripter']()
    float_widget = nuke.float_panels['vina_scripter']

    if panel_widget:
        panel_widget.scripter.console.update_output()

    float_widget.scripter.console.update_output()


def get_scripter_panel():
    panel_widget = nuke.panels['vina_scripter']()
    float_widget = nuke.float_panels['vina_scripter']

    if (panel_widget.isVisible() if panel_widget else False):
        return panel_widget
    else:
        return float_widget


def enter_node():
    scripter_panel = get_scripter_panel()
    node_inside = scripter_panel.scripter.enter_node()

    if node_inside and not scripter_panel.isVisible():
        scripter_panel.show()
        scripter_panel.scripter.console.clear_all()
        scripter_panel.scripter.editor.set_focus()


def edit_expression(tcl=False):
    scripter_panel = get_scripter_panel()
    scripter_panel.scripter.edit_expression(tcl)

    if not scripter_panel.isVisible():
        scripter_panel.show()
        scripter_panel.scripter.console.clear_all()
