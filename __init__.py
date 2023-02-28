from . import src as vina_scripter
from .nuke_util import panels

panels.init(vina_scripter.scripter.scripter_widget, 'Vina Scripter')
