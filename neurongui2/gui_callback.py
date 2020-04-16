from .gui import *
import logging
import warnings
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
        return 1
    def unmap(self, *args):
        self.mapped = False
        return 1

class graphProto:
    def __init__(self, *args):
        self.expressions = []
        self.mode = 0
    def __repr__(self):
        return 'GraphProto'
    def addexpr(self, expr):
        self.expressions.append(expr)
        print(self.expressions)
        return 1
    def plot(self, *args):
        for e in self.expressions:
            print(e+"\n")
        return 1
    def __del__(self):
        print("goodbye Graph")

def graphmode(mode):
    print('obsolete graphmode')
    print(mode)
    return 0

class TextEditor:
    def __init__(self, param):
        self.param = param
    def __repr__(self):
        return f'TextEditor{self.param}'
    def name(self):
        return self.param

def list_browser(the_list):
    print('list_browser:')
    print(the_list)
    #for i in range(len(the_list)):
        #print(the_list.o(i))
    return 1

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

class_map = {
    'HBox': HBox,
    'VBox': VBox,
    'Graph': Graph
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
    logging.debug("params: %r", (params,))
    
    # testing
    if fn == 'List.browser':
        return list_browser(obj)

    elif fn == 'TextEditor':
        return TextEditor(*params)
    elif fn == 'TextEditor.text':
        return obj.name()

    elif fn == 'graphmode':
        return graphmode(*params)

    elif fn == 'boolean_dialog':
        print('boolean dialog')
        print(params[0])
        print('0:', params[2])
        print('1:', params[1])
        return float(input('your choice: '))

    # general redirection
    try:
        if not obj:
            if fn in fn_map:
                return fn_map[fn](*params, context=context)
            elif fn in class_map:
                return class_map[fn](*params)
        else:
            split = fn.split('.')
            return getattr(obj, split[1])(*params)
    except:
        warnings.warn("redirection not set up for "+fn)

    return True
