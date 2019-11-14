import neuron
import gui
from neuron import rxd, units

_gui_functions = ('HBox', 'VBox', 'xpanel', 'xlabel', 'xbutton', 'xvalue', 'Graph')

class H:
    def __getattr__(self, var):
        if var in _gui_functions:
            return getattr(gui, var)
        else:
            return getattr(neuron.h, var)
    def __setattr__(self, var, val):
        setattr(neuron.h, var, val)

h = H()
