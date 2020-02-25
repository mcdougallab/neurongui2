import uuid
from neuron import h
import warnings

import logging
logging.basicConfig(level=logging.DEBUG, filename="mylog.txt")

make_browser_html = None

class Widget:
    def to_html(self):
        raise NotImplementedError()
    def mappings(self):
        return {}


class XValue(Widget):
    def __init__(self, prompt, variable):
        self.prompt = prompt
        if (isinstance(variable, str)):
            self.ptr = getattr(h, "_ref_" + variable)
        else:   #TODO: if not pointer
            self.ptr = variable
        self.uuid = uuid.uuid4().hex    # uuid4 because prob more secure than uuid1 

    def mappings(self):
        return {self.uuid: self.ptr}

    def to_html(self):
        return """<input type="number" data-variable="{}"><label> {}</label>""".format(self.uuid, self.prompt)

class XCheckBox(Widget):
    def __init__(self, prompt, state_variable, callback):
        self.prompt = prompt
        self.callback = callback
        self.state_ref = state_variable
        self.uuid = uuid.uuid4().hex    

    def mappings(self):
        return {self.uuid: self.state_ref}

    def to_html(self):
        if self.callback:
            return """<input type="checkbox" data-variable="{}" data-onclick="{}"><label> {}</label>""".format(self.uuid, self.callback, self.prompt)
        else:
            return """<input type="checkbox" data-variable="{}"><label> {}</label>""".format(self.uuid, self.prompt)


class XStateButton(Widget):
    def __init__(self, prompt, state_variable, callback):
        self.prompt = prompt
        self.callback = callback
        self.state_ref = state_variable
        self.uuid = uuid.uuid4().hex    

    def mappings(self):
        return {self.uuid: self.state_ref}

    def to_html(self):
        if self.callback:
            return """<button class="state" data-variable="{}" data-onclick="{}">{}</button>""".format(self.uuid, self.callback, self.prompt)
        else:
            return """<button class="state" data-variable="{}">{}</button>""".format(self.uuid, self.prompt)


class XButton(Widget): 
    def __init__(self, prompt, callback):
        self.prompt = prompt
        # In progress: making button inputs compatible
        if isinstance(callback, tuple):
            arg = callback[1]
            logging.debug("function: "+str(callback[0]))
            logging.debug("args: "+str(callback[1]))
            if isinstance(callback[1], tuple):
                self.callback = lambda: callback[0](*arg)
            else:
                self.callback = lambda: callback[0](arg)
        else:
            self.callback = callback
        self.uuid = uuid.uuid4().hex

    def mappings(self):
        return {self.uuid: self.callback}

    def to_html(self):
        return """<button data-onclick="{}">{}</button>""".format(self.uuid, self.prompt)

class XLabel(Widget):
    def __init__(self, text):
        self.text = text

    def mappings(self):
        return {}

    def to_html(self):
        return "{}".format(self.text)


class Container(Widget):
    def __init__(self):
        self.widgets = []
        self.orientation = 'vertical'

    def to_html(self):
        if self.orientation == 'horizontal':
            return '<div class="flex-container-h"><div>' + '</div><div>'.join(widget.to_html() for widget in self.widgets) + '</div></div>'
        else:
            return '<div class="flex-container-v"><div>' + '</div><div>'.join(widget.to_html() for widget in self.widgets) + '</div></div>'
    
    def add(self, item):
        self.widgets.append(item)
    
    def mappings(self):
        result = {}
        for widget in self.widgets:
            result.update(widget.mappings())
        return result
        

class Window(Container):
    def __init__(self, title):
        Container.__init__(self)
        self.title = title


class HBox(Container):
    def __init__(self):
        Container.__init__(self)
        self.orientation = 'horizontal'
    
    def intercept(self, value):
        if value:
            active_container.append(self)
        elif active_container[-1] != self and not value:
            # do nothing
            pass
        else:
            active_container.pop()
    
    def map(self):
        if not active_container:
            raise Exception('not currently supporting top-level HBox')

        if active_container[-1] == self:
            raise Exception('can only map to different container')

        active_container[-1].add(self)


class VBox(Container):
    def __init__(self):
        Container.__init__(self)
        self.orientation = 'vertical'
    
    def intercept(self, value):
        if value:
            active_container.append(self)
        elif active_container[-1] != self and not value:
            # do nothing
            pass
        else:
            active_container.pop()
    
    def map(self):
        if not active_container:
            raise Exception('not currently supporting top-level VBox')

        if active_container[-1] == self:
            raise Exception('can only map to different container')

        active_container[-1].add(self)

active_container = []

active_window = None


def xpanel(*args):
    global active_window
    if args and active_window is not None:
        raise Exception('not currently allowing nesting xpanels')
    if not args and active_window is None:
        raise Exception('no active xpanel')
    if args:
        active_window = Window(args[0])
        active_container.append(active_window)
    else:
        html = active_window.to_html()
        logging.debug(str(active_window.mappings()))
        make_browser_html(html, user_mappings=active_window.mappings(), title=active_window.title)
        active_window = None


def xvalue(prompt, variable):
    active_container[-1].add(XValue(prompt, variable))

def xcheckbox(prompt, state_variable, callback=None):
    active_container[-1].add(XCheckBox(prompt, state_variable, callback))

def xstatebutton(prompt, state_variable, callback=None):
    active_container[-1].add(XStateButton(prompt, state_variable, callback))

def xlabel(text):
    active_container[-1].add(XLabel(text))

def xbutton(prompt, callback):
    active_container[-1].add(XButton(prompt, callback))

class Graph(Widget): #TODO
    def __init__(self):
        self.label = []
        self.varname = []
        active_container[-1].add(self)

    def addvar(self, label, varname):
        self.label.append(label)
        self.varname.append(varname)

    def to_html(self):
        return """<div class="lineplot" data-x-var="h.t" data-y-var="{}" data-xlab="time (ms)" data-legendlabs="{}" style="width:300px; height:300px; border: 1px black solid"></div>""".format(";".join(self.varname), ";".join(self.label))

