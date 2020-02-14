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

"""def gui_callback(*args):
    global all_args
    all_args = args
    fn = args[0]
    obj = args[1]
    params = args[2:]
    if fn == 'VBox':
        return Box('V', *params)
    elif fn == 'HBox':
        return Box('H', *params)
    elif fn == 'Box.ismapped':
        return obj.ismapped()
    elif fn == 'Box.map':
        return obj.map(*params)
    elif fn == 'Box.unmap':
        return obj.unmap(*params)
    elif fn == 'List.browser':
        return list_browser(obj)
    elif fn == 'boolean_dialog':
        print('boolean dialog')
        print(params[0])
        print('0:', params[2])
        print('1:', params[1])
        return float(input('your choice: '))
    elif fn == 'xpanel':
        print('xpanel started')
        return True
    print('gui_callback')
    print(args)
    return True"""

fn_map = {
    'xpanel': xpanel,
    'xlabel': xlabel,
    'xvalue': xvalue,
    'xcheckbox': xcheckbox,
    'xstatebutton': xstatebutton,
    'xbutton': xbutton
}

def gui_callback(*args):
    global all_args
    all_args = args
    fn = args[0]
    obj = args[1]
    params = args[2:]
    logging.debug("fn: %s", fn)
    logging.debug("obj: %r", obj)
    logging.debug("params: %r", params)
    if fn in fn_map:
        fn_map[fn](*params)
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