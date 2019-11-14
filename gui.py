make_browser_html = None

class Widget:
    def to_html():
        raise NotImplementedError()


class XValue(Widget):
    def __init__(self, prompt, variable):
        self.prompt = prompt
        self.variable = variable

    def to_html(self):
        return """<input type="number" data-variable="{}"><label> {}</label>""".format(self.variable, self.prompt)


class XButton(Widget):
    def __init__(self, prompt, callback):
        self.prompt = prompt
        self.callback = callback

    def to_html(self):
        return """<button data-onclick="{}">{}</button>""".format(self.callback, self.prompt)

class XLabel(Widget):
    def __init__(self, text):
        self.text = text

    def to_html(self):
        return "{}".format(self.text)


class Container(Widget):
    def __init__(self):
        self.widgets = []
        self.orientation = 'vertical'

    def to_html(self):
        if self.orientation == 'horizontal':
            return '<table><tr><td>' + '</td>\n<td>'.join(widget.to_html() for widget in self.widgets) + '</td></tr></table>'
        else:
            return '<br/>\n'.join(widget.to_html() for widget in self.widgets)
    
    def add(self, item):
        self.widgets.append(item)
        

class Window(Container):
    def __init__(self, title):
        Container.__init__(self)
        self.title = title
        #self.orientation = 'horizontal'

    def get_active_container(self):
        # TODO: expand when allowing nesting
        return self


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
        active_window = None
        print(html)
        make_browser_html(html)


def xvalue(prompt, variable):
    active_container[-1].add(XValue(prompt, variable))


def xlabel(text):
    active_container[-1].add(XLabel(text))


def xbutton(prompt, callback):
    active_container[-1].add(XButton(prompt, callback))

class Graph(Widget):
    def __init__(self):
        self.label = []
        self.varname = []
        active_container[-1].add(self)

    def addvar(self, label, varname):
        self.label.append(label)
        self.varname.append(varname)

    def to_html(self):
        return """<div class="lineplot" data-x-var="h.t" data-y-var="{}" data-xlab="time (ms)" data-legendlabs="{}" style="width:300px; height:300px; border: 1px black solid"></div>""".format(";".join(self.varname), ";".join(self.label))

