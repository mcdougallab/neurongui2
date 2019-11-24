# browser code very lightly adapted from
# https://github.com/cztomczak/cefpython/blob/master/examples/wxpython.py

import wx
import wx.py.shell
from cefpython3 import cefpython as cef
import platform
import sys
import os
import base64
import threading
import time
import json
import copy
from weakref import WeakValueDictionary
from neuron import h, nrn_dll_sym
from neuron.units import ms, mV

h.load_file('stdrun.hoc')

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

if MAC:
    try:
        # noinspection PyUnresolvedReferences
        from AppKit import NSApp
    except ImportError:
        print("[wxpython.py] Error: PyObjC package is missing, "
              "cannot fix Issue #371")
        print("[wxpython.py] To install PyObjC type: "
              "pip install -U pyobjc")
        sys.exit(1)

# Configuration
WIDTH = 900
HEIGHT = 640

# Globals
g_count_windows = 0
browser_created_count = 0   #for the weak value dict of browsers
browser_weakvaldict = WeakValueDictionary()

# for tracking initializing simulations
def finit_handler():
    global browser_weakvaldict
    for b in browser_weakvaldict.values():
        b.fih = 1

FIH = h.FInitializeHandler(finit_handler)

def html_to_data_uri(html, browser_id, js_callback=None):
    # This function is called in two ways:
    # 1. From Python: in this case value is returned
    # 2. From Javascript: in this case value cannot be returned because
    #    inter-process messaging is asynchronous, so must return value
    #    by calling js_callback.
    html = html.replace("BROWSER_ID_GOES_HERE", str(browser_id))
    html = html.encode("utf-8", "replace")
    b64 = base64.b64encode(html).decode("utf-8", "replace")
    ret = "data:text/html;base64,{data}".format(data=b64)
    if js_callback:
        js_print(js_callback.GetFrame().GetBrowser(),
                 "Python", "html_to_data_uri",
                 "Called from Javascript. Will call Javascript callback now.")
        js_callback.Call(ret)
    else:
        return ret

def main():
    check_versions()
    #sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    settings = {}
    if MAC:
        # Issue #442 requires enabling message pump on Mac
        # and calling message loop work in a timer both at
        # the same time. This is an incorrect approach
        # and only a temporary fix.
        settings["external_message_pump"] = True

        # argv[0] is used by default in Mac to populate the program menu
        # e.g. Hide Neuron, Quit Neuron
        sys.argv[0] = 'NEURON'

        # TODO: apparently need to create an app to have the mac menubar program name say something other than python
        # see https://stackoverflow.com/questions/12633100/changing-wxpython-app-mac-menu-bar-title
        # This might not be a big deal, given that NEURON is already an app?

    if WINDOWS:
        # noinspection PyUnresolvedReferences, PyArgumentList
        cef.DpiAware.EnableHighDpiSupport()
    cef.Initialize(settings=settings)
    app = CefApp(False)
    app.MainLoop()
    del app  # Must destroy before calling Shutdown
    if not MAC:
        # On Mac shutdown is called in OnClose
        cef.Shutdown()


def check_versions():
    """print("[wxpython.py] CEF Python {ver}".format(ver=cef.__version__))
    print("[wxpython.py] Python {ver} {arch}".format(
            ver=platform.python_version(), arch=platform.architecture()[0]))
    print("[wxpython.py] wxPython {ver}".format(ver=wx.version()))"""
    # CEF Python version requirement
    assert cef.__version__ >= "66.0", "CEF Python v66.0+ required to run this"


def scale_window_size_for_high_dpi(width, height):
    """Scale window size for high DPI devices. This func can be
    called on all operating systems, but scales only for Windows.
    If scaled value is bigger than the work area on the display
    then it will be reduced."""
    if not WINDOWS:
        return width, height
    (_, _, max_width, max_height) = wx.GetClientDisplayRect().Get()
    # noinspection PyUnresolvedReferences
    (width, height) = cef.DpiAware.Scale((width, height))
    if width > max_width:
        width = max_width
    if height > max_height:
        height = max_height
    return width, height

class NEURONFrame(wx.Frame):
    def voltage_axis(self, *args, **kwargs):
        print('voltage_axis')
        print('args:', args)
        print('kwargs:', kwargs)

    def run_script(self, *args, **kwargs):
        # TODO: we clear entire commands from the shell before running the script
        #       but only restore the active
        #       stdout is currently going INTO THE PROMPT (so then when you hit enter you probably get a syntax error)
        with wx.FileDialog(self,
                        'Select script to run',
                        wildcard="All runnable files (*.py; *.hoc; *.ses)|*.py;*.hoc;*.ses|Python files (*.py);*.py|HOC files (*.hoc);*.hoc|Session files (*.ses);*.ses",
                        style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # cancelled
            path = file_dialog.GetPath()
        extension = os.path.splitext(path)[1]
        current_shell.redirectStdout(True)
        current_shell.redirectStdin(True)
        current_shell.redirectStderr(True)
        # store the old command
        #old_command = current_shell.getMultilineCommand()
        old_command = current_shell.getCommand()
        current_shell.clearCommand()
        current_shell.write('\n')
        if extension == '.py':
            with open(path) as f:
                code = compile(f.read(), path, 'exec')
            current_shell.interp.runcode(code)
        elif extension in ('.hoc', '.ses'):
            # the True means it will always run, even if it has already been run
            h.load_file(True, path)
        else:
            print('undefined file:', path)
            # TODO: how should we handle "impossible" errors like this?
        # restore the prompt state
        current_shell.prompt()
        current_shell.write(old_command)
    
    def exit(self, *args, **kwargs):
        # TODO: put any are-you-sure questions here
        sys.exit()

    def create_menu(self):
        filemenu = wx.Menu()
        run_script_menuitem = filemenu.Append(1, "&Run script\tCtrl+O")
        self.Bind(wx.EVT_MENU, self.run_script, run_script_menuitem)
        exit_menuitem = filemenu.Append(wx.ID_EXIT, "E&xit")
        self.Bind(wx.EVT_MENU, self.exit, exit_menuitem)
        graph_menu = wx.Menu()
        voltage_axis_menuitem = graph_menu.Append(2, "&Voltage Axis")
        self.Bind(wx.EVT_MENU, self.voltage_axis, voltage_axis_menuitem)
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        menubar.Append(graph_menu, "&Graph")
        self.SetMenuBar(menubar)

class NEURONWindow(NEURONFrame):

    def __init__(self, html_file=None, user_mappings={}, html=None, title=''):
        self.browser = None
        self.html_file = html_file
        self.user_mappings = user_mappings
        self.rel_vars = []
        self.graph_vars = {}    # graph vector dictionary
        self.fih = 0    # tracker for whether fInitialize has happened
        self.t_tracker = 0  #tracker for length of time (or other) vector
        self.ready_status = 1   #browser sends signal that it's ready when done updating graphs
        self.data_waiting = None    #graph data waiting for browser to be ready
        self.t_tracker_vec = "h.t"  #which vector to use for graph tracking

        if html_file is not None and html is not None:
            raise Exception("specify either html_file or html")

        if html is None:
            with open(html_file) as f:
                my_html = f.read()
        else:
            my_html = html

        with open("main_script.html") as f:
            my_wrapper_html = f.read()

        self.wrapper_html = my_wrapper_html.replace("HTML_GOES_HERE", my_html)

        # Must ignore X11 errors like 'BadWindow' and others by
        # installing X11 error handlers. This must be done after
        # wx was intialized.
        if LINUX:
            cef.WindowUtils.InstallX11ErrorHandlers()

        global g_count_windows
        g_count_windows += 1

        size = scale_window_size_for_high_dpi(WIDTH, HEIGHT)

        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY,
                          title=title, size=size)

        self.setup_icon()
        self.create_menu()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Set wx.WANTS_CHARS style for the keyboard to work.
        # This style also needs to be set for all parent controls.
        self.browser_panel = wx.Panel(self, style=wx.WANTS_CHARS)
        self.browser_panel.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.browser_panel.Bind(wx.EVT_SIZE, self.OnSize)

        if MAC:
            # Make the content view for the window have a layer.
            # This will make all sub-views have layers. This is
            # necessary to ensure correct layer ordering of all
            # child views and their layers. This fixes Window
            # glitchiness during initial loading on Mac (Issue #371).
            NSApp.windows()[0].contentView().setWantsLayer_(True)

        if LINUX:
            # On Linux must show before embedding browser, so that handle
            # is available (Issue #347).
            self.Show()
            # In wxPython 3.0 and wxPython 4.0 on Linux handle is
            # still not yet available, so must delay embedding browser
            # (Issue #349).
            if wx.version().startswith("3.") or wx.version().startswith("4."):
                wx.CallLater(100, self.embed_browser)
            else:
                # This works fine in wxPython 2.8 on Linux
                self.embed_browser()
        else:
            self.embed_browser()
            self.Show()

    def setup_icon(self):
        icon_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 "resources", "wxpython.png")
        # wx.IconFromBitmap is not available on Linux in wxPython 3.0/4.0
        if os.path.exists(icon_file) and hasattr(wx, "IconFromBitmap"):
            icon = wx.IconFromBitmap(wx.Bitmap(icon_file, wx.BITMAP_TYPE_PNG))
            self.SetIcon(icon)

    def embed_browser(self):
        global browser_created_count, browser_weakvaldict
        self.browser_id = browser_created_count

        window_info = cef.WindowInfo()
        (width, height) = self.browser_panel.GetClientSize().Get()
        assert self.browser_panel.GetHandle(), "Window handle not available"
        window_info.SetAsChild(self.browser_panel.GetHandle(),
                               [0, 0, width, height])
        self.browser = cef.CreateBrowserSync(window_info,
                                             url=html_to_data_uri(self.wrapper_html, self.browser_id))
        self.set_browser_callbacks()
        self.browser.SetClientHandler(FocusHandler())
        browser_weakvaldict[self.browser_id] = self # create mapping to frame object in weak value dict

    def set_browser_callbacks(self):
        self.bindings = cef.JavascriptBindings(bindToFrames=True, bindToPopups=True)
        self.bindings.SetFunction("_print_to_terminal", _print_to_terminal)
        self.bindings.SetFunction("_update_vars", _update_vars)
        self.bindings.SetFunction("_py_function_handler", _py_function_handler)
        self.bindings.SetFunction("_set_relevant_vars", _set_relevant_vars)
        self.bindings.SetFunction("_flag_browser_ready", _flag_browser_ready)
        self.browser.SetJavascriptBindings(self.bindings)

    def OnSetFocus(self, _):
        if not self.browser:
            return
        if WINDOWS:
            cef.WindowUtils.OnSetFocus(self.browser_panel.GetHandle(),
                                       0, 0, 0)
        self.browser.SetFocus(True)

    def OnSize(self, _):
        if not self.browser:
            return
        if WINDOWS:
            cef.WindowUtils.OnSize(self.browser_panel.GetHandle(),
                                   0, 0, 0)
        elif LINUX:
            (x, y) = (0, 0)
            (width, height) = self.browser_panel.GetSize().Get()
            self.browser.SetBounds(x, y, width, height)
        self.browser.NotifyMoveOrResizeStarted()

    def OnClose(self, event):
        if not self.browser:
            # May already be closing, may be called multiple times on Mac
            return

        if MAC:
            # On Mac things work differently, other steps are required
            self.monitor_loop.running = False
            self.browser.CloseBrowser()
            self.clear_browser_references()
            self.Destroy()
            global g_count_windows
            g_count_windows -= 1
            if g_count_windows == 0:
                cef.Shutdown()
                wx.GetApp().ExitMainLoop()
                # Call _exit otherwise app exits with code 255 (Issue #162).
                # noinspection PyProtectedMember
                os._exit(0)
        else:
            # Calling browser.CloseBrowser() and/or self.Destroy()
            # in OnClose may cause app crash on some paltforms in
            # some use cases, details in Issue #107.
            self.monitor_loop.running = False
            self.browser.ParentWindowWillClose()
            event.Skip()
            self.clear_browser_references()

    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.browser = None


class FocusHandler(object):
    def OnGotFocus(self, browser, **_):
        # Temporary fix for focus issues on Linux (Issue #284).
        if LINUX:
            #print("[wxpython.py] FocusHandler.OnGotFocus:"
            #      " keyboard focus fix (Issue #284)")
            browser.SetFocus(True)


class CefApp(wx.App):

    def __init__(self, redirect):
        self.timer = None
        self.timer_id = 1
        self.is_initialized = False
        super(CefApp, self).__init__(redirect=redirect)
        self.SetAppDisplayName('NEURON')
        self.SetAppName('NEURON')


    def OnPreInit(self):
        super(CefApp, self).OnPreInit()
        # On Mac with wxPython 4.0 the OnInit() event never gets
        # called. Doing wx window creation in OnPreInit() seems to
        # resolve the problem (Issue #350).
        if MAC and wx.version().startswith("4."):
            #print("[wxpython.py] OnPreInit: initialize here"
            #      " (wxPython 4.0 fix)")
            self.initialize()

    def OnInit(self):
        self.initialize()
        return True

    def initialize(self):
        if self.is_initialized:
            return
        self.is_initialized = True
        self.create_timer()
        make_terminal()

    def create_timer(self):
        # See also "Making a render loop":
        # http://wiki.wxwidgets.org/Making_a_render_loop
        # Another way would be to use EVT_IDLE in NEURONWindow.
        self.timer = wx.Timer(self, self.timer_id)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(10)  # 10ms timer

    def on_timer(self, _):
        cef.MessageLoopWork()

    def OnExit(self):
        self.timer.Stop()
        return 0


_all_windows = []
current_shell = None

# TODO: incorporate g_count_windows logic
def make_terminal():
    global current_shell
    window = NEURONFrame(None, title="Console [{}]".format(len(_all_windows) + 1), size=(600, 400))
    # by explicitly specifying the locals, we couple the shells together
    # while simultaneously keeping them unable to directly access our code
    # hmm... maybe a bad idea; should we transfer over a gui variable?
    shell = wx.py.shell.Shell(parent=window, locals=shared_locals)
    window.create_menu()
    _all_windows.append(shell)
    shared_locals['shell'] = shell
    current_shell = shell
    shell.run("print('Type make_terminal() or make_browser() or quit()')", verbose=False, prompt=False)
    #shell.write("Type make_terminal() or make_browser() or quit()\n")
    window.Show(True) 

def make_browser_html(html, user_mappings={}, title=''):
    global browser_created_count
    browser_created_count += 1
    frame = NEURONWindow(user_mappings=user_mappings, html=html, title=title)
    frame.Show()
    _all_windows.append(frame)
    return frame

def make_browser(html_file, user_mappings={}):
    global browser_created_count
    browser_created_count += 1
    frame = NEURONWindow(html_file, user_mappings)
    frame.Show()
    _all_windows.append(frame)
    return frame

class LoopTimer(threading.Thread) :
  """
  a Timer that calls f every interval
  """
  def __init__(self, interval, fun, *param) :
    """
    @param interval: time in seconds between call to fun(
    @param fun: the function to call on timer update
    """
    self.started = False
    self.interval = interval
    self.fun = fun
    self.param = param
    threading.Thread.__init__(self)
    self.setDaemon(True)

  def run(self) :
    self.started = True
    self.running = True
    while self.running==True:
      self.fun(*self.param)
      time.sleep(self.interval)

def monitor_browser_vars(this_browser):
    locals_copy = {} # initiate but don't know rel_vars yet
    timer = LoopTimer(0.1, _update_browser_vars, this_browser, locals_copy)
    timer.start()
    return timer

def _print_to_terminal():
    # experimental info relayed to terminal from browser action
    print("So this worked.")

def _py_function_handler(browser_id, function_string):
    global browser_weakvaldict 
    # first check user mappings then shared_locals for the function
    exec(function_string, shared_locals, browser_weakvaldict[browser_id].user_mappings)

def _flag_browser_ready(browser_id):
    global browser_weakvaldict
    browser_weakvaldict[browser_id].ready_status = 1

def lookup(this_browser, variable, action, newValue=None):
    mappings =  this_browser.user_mappings
    # repeated process to check for a variable in a particular browser's mappings and then shared_locals
    # action can be "get" or "set"; newValue is value to set
    split = variable.split('.')
    if len(split) == 1:
        # single variable
        if variable in mappings.keys():
            if action == "get":
                return mappings.get(variable)
            elif action =="set":
                mappings[variable] = newValue
        elif variable in shared_locals.keys():
            if action == "get":
                return shared_locals.get(variable)
            elif action == "set":
                shared_locals[variable] = newValue
        else:
            print("unknown variable: ", variable)
            return None
    else:
        # if it's an attribute of an object
        obj, attribute = split
        if obj in mappings.keys():
            if action == "get":
                return getattr(mappings[obj], attribute)
            elif action == "set":
                setattr(mappings[obj], attribute, newValue)
        elif obj in shared_locals.keys():
            if action == "get":
                return getattr(shared_locals[obj], attribute)
            elif action == "set":
                setattr(shared_locals[obj], attribute, newValue)
        else:
            print("unknown variable: ", variable)
            return None

def lookup_graph_var(this_browser, variable):
    # specifically for graph vector variables; only to retrieve
    # _ref_ attributes
    mappings = this_browser.user_mappings
    obj, attribute = variable.split('.')
    if obj in mappings.keys():
        return getattr(mappings[obj], "_ref_"+attribute)
    elif obj in shared_locals.keys():
        return getattr(shared_locals[obj], "_ref_"+attribute)
    else:
        print("unknown variable: ", variable)
        return None

def _update_vars(browser_id, variable, value):
    global browser_weakvaldict
    # update any variables sent in by the browser
    #TODO: consider; # can this lead to discrepancies betw shared_locals and user_mappings?
    if value == '':
        value = None
    lookup(browser_weakvaldict[browser_id], variable, "set", float(value))

def _set_relevant_vars(to_update):
    global browser_weakvaldict
    # receive JS declaration of relevant variables
    rel_vars, graph_vars, browser_id = json.loads(to_update)
    this_browser = browser_weakvaldict[browser_id]

    this_browser.rel_vars = rel_vars
    for g_var in graph_vars:
        # set up recording graph vector variables
        this_browser.graph_vars[g_var] = h.Vector().record(lookup_graph_var(this_browser, g_var))

    # tracking data changing for graphs
    if graph_vars:  # if there are any graphs, keep track
        t_vec = this_browser.graph_vars.get("h.t")
        if t_vec:
            this_browser.t_tracker = len(t_vec) # or just initialize to zero?
        else:
            this_browser.t_tracker = len(this_browser.graph_vars.get(graph_vars[0]))  #use whatever is the first vector; length is still time
            this_browser.t_tracker_vec = graph_vars[0]

    this_browser.monitor_loop = monitor_browser_vars(this_browser)
    

def delete_var(v):
    del shared_locals[v]

def find_changed_vars(this_browser, old_copy):
    # input is copy of relevant variable dict and latest shared_locals; find which are changed or deleted
    changed = {}
    deleted = []
    rel_vars = this_browser.rel_vars
    for v in rel_vars:
        current = lookup(this_browser, v, "get")
        if (current is None) and (v in old_copy.keys()):
            deleted.append(v)
        elif current != old_copy.get(v):
            if isinstance(current, list):
                changed[v] = copy.copy(current)
            else:
                changed[v] = current
    return [changed, deleted]

def send_graph_vars(this_browser, action):
    # action is either make or update
    to_send = {}
    graph_vars = this_browser.graph_vars
    for k in graph_vars.keys():
        if action == "make":
            to_send[k] = list(graph_vars[k])
        elif action == "update":
            to_send[k] = list(graph_vars[k])[this_browser.t_tracker:]  # only the new data
    this_browser.browser.ExecuteJavascript("update_graph_vectors({}, {})".format(json.dumps(to_send), json.dumps([action])))

def _update_browser_vars(this_browser, locals_copy):  
    # create dictionary of the changed variables 
    changed_vars, deleted_vars = find_changed_vars(this_browser, locals_copy)
    locals_copy.update(changed_vars)
    # handle deletions separately
    for d in deleted_vars:
        del locals_copy[d]
    # update the changed variables for javascript
    if changed_vars or deleted_vars:
        this_browser.browser.ExecuteJavascript("update_html_variable_displays({}, {})".format(json.dumps(changed_vars), json.dumps(deleted_vars)))
    # handle graph vectors - if browser ready and there are graphs
    if this_browser.graph_vars:
        current_lengthT = len(this_browser.graph_vars.get(this_browser.t_tracker_vec))
        if this_browser.ready_status == 1:
            #send if finitialize has been called or h.t has changed
            if this_browser.fih == 1:
                # t_tracker has not been updated since last data sent, so will send ALL new data
                this_browser.ready_status = 0
                send_graph_vars(this_browser, 'make')
                this_browser.fih = 0
                this_browser.t_tracker = current_lengthT
            elif current_lengthT != this_browser.t_tracker:
                this_browser.ready_status = 0
                send_graph_vars(this_browser, 'update')
                this_browser.t_tracker = current_lengthT

def setupSim():
    shared_locals['shell'].runfile('setup.txt')

shared_locals = {'make_terminal': make_terminal, 'make_browser': make_browser, 'quit': sys.exit, 'delete_var':delete_var,
'weakdict':browser_weakvaldict, 'sim': lambda: make_browser("simulation1.html"), 'setupSim':setupSim}

# todo: should this be here or in main
import gui
gui.make_browser_html = make_browser_html

if __name__ == '__main__':
    main()
