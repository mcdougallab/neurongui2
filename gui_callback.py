from gui import *
import logging
logging.basicConfig(level=logging.DEBUG, filename="mylog.txt")

class Box:
    def __init__(self, orientation, *args):
        self.mapped = False
        self.orientation = orientation
    def __repr__(self):
        return 'Py{}Box'.format(self.orientation)
    def ismapped(self):
        return self.mapped
    def map(self, *args):
        self.mapped = True
        return True
    def unmap(self, *args):
        self.mapped = False
        return True

class TextEditor:
    def __init__(self, param):
        self.param = param
    def __repr__(self):
        return f'TextEditor{self.param}'
    def name(self):
        return self.param

class graphProto:
    def __init__(self, *args):
        self.expressions = []
        self.mode = 0
    def __repr__(self):
        return 'GraphProto'
    def addexpr(self, expr):
        self.expressions.append(expr)
        print(self.expressions)
        return True
    def plot(self, *args):
        for e in self.expressions:
            print(e+"\n")
        return True

def graphmode(mode):
    print('obsolete graphmode')
    print(mode)
    return 0

def list_browser(the_list):
    print('list_browser:')
    print(the_list)
    for i in range(len(the_list)):
        print(the_list.o(i))
    return True

fn_map = {
    'xpanel': xpanel,
    'xlabel': xlabel,
    'xvalue': xvalue,
    'xcheckbox': xcheckbox,
    'xstatemenu': xstatebutton,
    'xbutton': xbutton,
    'xpvalue': xvalue,
    'xvarlabel': xvarlabel
}

def gui_callback(*args):
    global all_args
    all_args = args
    fn = args[0]
    obj = args[1]
    context = args[2]
    params = args[3:]
    logging.debug("fn: %s", fn)
    logging.debug("obj: %r", obj)
    logging.debug("params: %r", params)
    if fn in fn_map:
        return fn_map[fn](*params, context=context)

    elif fn == 'VBox':
        return VBox(*params)
    elif fn == 'HBox':
        return HBox(*params)
    elif fn == 'Box.map':
        return obj.map(*params)
    elif fn == 'Box.intercept':
        return obj.intercept(*params)

    elif fn == 'List.browser':
        return list_browser(obj)

    elif fn == 'TextEditor':
        return TextEditor(*params)
    elif fn == 'TextEditor.text':
        return obj.name()

    elif fn == 'Graph':
        return Graph(*params)
    elif fn == 'Graph.addvar':
        return obj.addvar(*params)

    elif (fn == "doNotify") or (fn == "doEvents"):
        print(fn)
        return 0

    elif fn == 'graphmode':
        return graphmode(*params)

    elif fn == 'boolean_dialog':
        print('boolean dialog')
        print(params[0])
        print('0:', params[2])
        print('1:', params[1])
        return float(input('your choice: '))
    logging.debug("do something else (nothing given to do)")
    return True

"""
DEBUG:root:fn: VBox
DEBUG:root:obj: None
DEBUG:root:params: ('Neuron',)
DEBUG:root:fn: Box.ismapped
DEBUG:root:obj: PyVBox
DEBUG:root:params: ()
DEBUG:root:fn: Box.map
DEBUG:root:obj: PyVBox
DEBUG:root:params: ()
DEBUG:root:fn: Box.ismapped
DEBUG:root:obj: <list_iterator object at 0x7f863f912fd0>
DEBUG:root:params: ()


# for testing
elif fn == 'Graph':
    return graphProto(*params)
elif fn == 'Graph.addexpr':
    return obj.addexpr(*params)
elif fn == 'Graph.plot':
    return obj.plot(*params)"""

# real graph testing
"""elif fn == 'Graph':
    return Graph(*params)
elif fn == 'Graph.addvar':
    return obj.addvar(*params)"""

# for testing purposes
"""elif fn == 'VBox':
    return Box('V', *params)
elif fn == 'HBox':
    return Box(*params)
elif fn == 'Box.ismapped':
    return obj.ismapped()
elif fn == 'Box.map':
    return obj.map(*params)
elif fn == 'Box.unmap':
    return obj.unmap(*params)"""
