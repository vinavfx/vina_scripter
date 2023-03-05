from . import src as vina_scripter
from .nuke_util import panels

def setup():
    panels.init('vina_scripter.vina_scripter.scripter.scripter_widget', 'Vina Scripter')
