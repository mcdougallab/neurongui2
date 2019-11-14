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

    def to_html(self):
        return '<br/>\n'.join(widget.to_html() for widget in self.widgets)
    
    def add(self, item):
        self.widgets.append(item)
        

class Window(Container):
    def __init__(self, title):
        Container.__init__(self)
        self.title = title

    def get_active_container(self):
        # TODO: expand when allowing nesting
        return self


active_window = None


def xpanel(*args):
    global active_window
    if args and active_window is not None:
        raise Exception('not currently allowing nesting xpanels')
    if not args and active_window is None:
        raise Exception('no active xpanel')
    if args:
        active_window = Window(args[0])
    else:
        html = active_window.to_html()
        active_window = None
        make_browser_html(html)


def xvalue(prompt, variable):
    active_window.get_active_container().add(XValue(prompt, variable))


def xlabel(text):
    active_window.get_active_container().add(XLabel(text))


def xbutton(prompt, callback):
    active_window.get_active_container().add(XButton(prompt, callback))
