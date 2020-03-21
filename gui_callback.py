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

def list_browser(the_list):
    print('list_browser:')
    for i in range(len(the_list)):
        print(the_list.o(i))
    return True

fn_map = {
    'xpanel': xpanel,
    'xlabel': xlabel,
    'xvalue': xvalue,
    'xcheckbox': xcheckbox,
    'xstatebutton': xstatebutton,
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
    #logging.debug("fn: %s", fn)
    #logging.debug("obj: %r", obj)
    #logging.debug("params: %r", params)
    if fn in fn_map:
        fn_map[fn](*params, context=context)
        return True
    elif fn == 'List.browser':
        return list_browser(obj)
    elif fn == 'boolean_dialog':
        print('boolean dialog')
        print(params[0])
        print('0:', params[2])
        print('1:', params[1])
        return float(input('your choice: '))
    print('do something else')
    return True

