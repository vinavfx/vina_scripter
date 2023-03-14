from . import src as vina_scripter
from .nuke_util import panels


def setup():
    panels.init(
        'vina_scripter.vina_scripter.scripter_panel.panel_scripter', 'Vina Scripter')

    panels.init_float_panel(
        vina_scripter.scripter_panel.float_scripter, 'vina_scripter')
