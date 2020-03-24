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
    def __init__(self, prompt, variable, boolean_deflt, action, boolean_canrun):
        self.prompt = prompt
        if (isinstance(variable, str)):
            self.ptr = getattr(h, "_ref_" + variable)
        else:   #TODO: if not pointer
            self.ptr = variable
        self.uuid = uuid.uuid4().hex    # uuid4 because prob more secure than uuid1 

        if boolean_deflt:
            # TODO add a checkbox that is checked when value is not at default
            # involves a state variable for checkbox and storing original value somewhere
            warnings.warn("Checkbox tied to xvalue not yet implemented.")
        self.callback = None
        if action is not None:
            self.uuid2 = uuid.uuid4().hex
            if isinstance(callback, tuple): 
                arg = callback[1]
                if isinstance(callback[1], tuple):
                    self.callback = lambda: callback[0](*arg)
                else:
                    self.callback = lambda: callback[0](arg)
            else:
                self.callback = callback
        if boolean_canrun:
            # TODO change the label to a button, callback when either button is pressed or value is changed
            warnings.warn("Xvalue callback button appearances not yet implemented.")

    def mappings(self):
        if self.callback:
            return{self.uuid: self.ptr, self.uuid2: self.callback}
        else:
            return {self.uuid: self.ptr}

    def to_html(self):
        if self.callback:
            return """<input type="number" data-variable="{}" data-onenter="{}"><label> {}</label>""".format(self.uuid, self.uuid2, self.prompt)
        else:
            return """<input type="number" data-variable="{}"><label> {}</label>""".format(self.uuid, self.prompt)

class XCheckBox(Widget):
    def __init__(self, prompt, state_variable, callback):
        self.prompt = prompt
        self.state_ref = state_variable
        if isinstance(callback, tuple): 
            arg = callback[1]
            if isinstance(callback[1], tuple):
                self.callback = lambda: callback[0](*arg)
            else:
                self.callback = lambda: callback[0](arg)
        else:
            self.callback = callback

        self.uuid = uuid.uuid4().hex    
        self.uuid2 = uuid.uuid4().hex

    def mappings(self):
        if self.callback:
            return {self.uuid: self.state_ref, self.uuid2: self.callback}
        else:
            return {self.uuid: self.state_ref}

    def to_html(self):
        if self.callback:
            return """<label class="checkbox"><input type="checkbox" data-variable="{}" data-onclick="{}"> {}</label>""".format(self.uuid, self.uuid2, self.prompt)
        else:
            return """<label class="checkbox"><input type="checkbox" data-variable="{}"> {}</label>""".format(self.uuid, self.prompt)


class XStateButton(Widget):
    def __init__(self, prompt, state_variable, callback):
        self.prompt = prompt
        self.state_ref = state_variable
        if isinstance(callback, tuple): # allow input on callback. Unlikely for statebutton but available.
            arg = callback[1]
            if isinstance(callback[1], tuple):
                self.callback = lambda: callback[0](*arg)
            else:
                self.callback = lambda: callback[0](arg)
        else:
            self.callback = callback

        self.uuid = uuid.uuid4().hex   
        self.uuid2 = uuid.uuid4().hex 

    def mappings(self):
        if self.callback:
            return {self.uuid: self.state_ref, self.uuid2: self.callback}
        else:
            return {self.uuid: self.state_ref}

    def to_html(self):
        if self.callback:
            return """<button class="state" data-variable="{}" data-onclick="{}">{}</button>""".format(self.uuid, self.uuid2, self.prompt)
        else:
            return """<button class="state" data-variable="{}">{}</button>""".format(self.uuid, self.prompt)


class XButton(Widget): 
    def __init__(self, prompt, callback):
        self.prompt = prompt
        if isinstance(callback, tuple):
            arg = callback[1]
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

class XVarLabel(Widget):
    def __init__(self, strref):
        self.strref = strref
        self.uuid = uuid.uuid4().hex

    def mappings(self):
        return {self.uuid: self.strref}

    def to_html(self):
        return """<label class="xvarlabel" data-variable={}> </label>""".format(self.uuid)


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


def xpanel(*args, context=None):
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
        #logging.debug(str(active_window.mappings()))
        make_browser_html(html, user_mappings=active_window.mappings(), title=active_window.title)
        active_window = None
    return 0


def xvalue(prompt, variable, boolean_deflt=None, action=None, boolean_canrun=None, context=None):
    active_container[-1].add(XValue(prompt, variable, boolean_deflt, action, boolean_canrun))
    return 0

def xcheckbox(prompt, state_variable, callback=None, context=None):
    active_container[-1].add(XCheckBox(prompt, state_variable, callback))
    return 0

def xstatebutton(prompt, state_variable, callback=None, context=None):
    active_container[-1].add(XStateButton(prompt, state_variable, callback))
    return 0

def xlabel(text, context=None):
    active_container[-1].add(XLabel(text))
    return 0

def xbutton(prompt, callback, context=None):
    active_container[-1].add(XButton(prompt, callback))
    return 0

def xvarlabel(strref, context=None):
    active_container[-1].add(XVarLabel(strref))
    return 0

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

