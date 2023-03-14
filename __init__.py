# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
import nuke

from . import src as vina_scripter
from .nuke_util import panels

from .src.script_output import get_nuke_console


nuke_console = None

def setup():
    panels.init(
        'vina_scripter.vina_scripter.scripter_panel.panel_scripter', 'Vina Scripter')

    panels.init_float_panel(
        vina_scripter.scripter_panel.float_scripter, 'vina_scripter')

    nuke.menu('Nuke').addCommand(
        'Edit/Node/Edit Script ( Knob Scripter )', enter_node, 'alt+z')

    nuke.menu('Animation').addCommand(
        'Python Expression', 'vina_scripter.edit_expression()')

    nuke.menu('Animation').addCommand(
        'Tcl Expression', 'vina_scripter.edit_expression(True)')

    nuke.addUpdateUI(connect_to_nuke_console)


def connect_to_nuke_console():
    global nuke_console

    if nuke_console:
        return

    nuke_console = get_nuke_console()

    if not nuke_console:
        return

    nuke_console.textChanged.connect(update_consoles)


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


def edit_expression(tcl=False):
    scripter_panel = get_scripter_panel()
    scripter_panel.scripter.edit_expression(tcl)

    if not scripter_panel.isVisible():
        scripter_panel.show()
        scripter_panel.scripter.console.clear_all()
