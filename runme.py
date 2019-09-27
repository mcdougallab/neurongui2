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
from neuron import h

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

with open('simple.html') as f:
    my_html = f.read()

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


class MainFrame(wx.Frame):

    def __init__(self):
        self.browser = None

        # Must ignore X11 errors like 'BadWindow' and others by
        # installing X11 error handlers. This must be done after
        # wx was intialized.
        if LINUX:
            cef.WindowUtils.InstallX11ErrorHandlers()

        global g_count_windows
        g_count_windows += 1

        size = scale_window_size_for_high_dpi(WIDTH, HEIGHT)

        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY,
                          title='a browser window!', size=size)

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

    def create_menu(self):
        filemenu = wx.Menu()
        filemenu.Append(1, "Some option")
        filemenu.Append(2, "Another option")
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        self.SetMenuBar(menubar)

    def embed_browser(self):
        global browser_created_count, browser_weakvaldict
        self.browser_id = browser_created_count

        window_info = cef.WindowInfo()
        (width, height) = self.browser_panel.GetClientSize().Get()
        assert self.browser_panel.GetHandle(), "Window handle not available"
        window_info.SetAsChild(self.browser_panel.GetHandle(),
                               [0, 0, width, height])
        self.browser = cef.CreateBrowserSync(window_info,
                                             url=html_to_data_uri(my_html, self.browser_id))
        self.set_browser_callbacks()
        self.browser.SetClientHandler(FocusHandler())
        browser_weakvaldict[self.browser_id] = self # create mapping to frame object in weak value dict

    def set_browser_callbacks(self):
        self.bindings = cef.JavascriptBindings(bindToFrames=True, bindToPopups=True)
        self.bindings.SetFunction("_print_to_terminal", _print_to_terminal)
        self.bindings.SetFunction("_update_vars", _update_vars)
        self.bindings.SetFunction("_py_function_handler", _py_function_handler)
        self.bindings.SetFunction("_set_relevant_vars", _set_relevant_vars)
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
        # Another way would be to use EVT_IDLE in MainFrame.
        self.timer = wx.Timer(self, self.timer_id)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(10)  # 10ms timer

    def on_timer(self, _):
        cef.MessageLoopWork()

    def OnExit(self):
        self.timer.Stop()
        return 0


_all_windows = []

# TODO: incorporate g_count_windows logic
def make_terminal():
    window = wx.Frame(None, title="Console [{}]".format(len(_all_windows) + 1), size=(600, 400))
    # by explicitly specifying the locals, we couple the shells together
    # while simultaneously keeping them unable to directly access our code
    # hmm... maybe a bad idea; should we transfer over a gui variable?
    shell = wx.py.shell.Shell(parent=window, locals=shared_locals)
    _all_windows.append(shell)
    shared_locals['shell'] = shell
    shell.run("print('Type make_terminal() or make_browser() or quit()')", verbose=False, prompt=False)
    #shell.write("Type make_terminal() or make_browser() or quit()\n")
    window.Show(True) 

def make_browser():
    global browser_created_count
    browser_created_count += 1
    frame = MainFrame()
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

def monitor_browser_vars(browser):
    locals_copy = {} # initiate but don't know rel_vars yet
    timer = LoopTimer(0.1, _update_browser_vars, browser, locals_copy)
    timer.start()
    return timer

def _print_to_terminal():
    # experimental info relayed to terminal from browser action
    print("So this worked.")

def _py_function_handler(function_string):
    exec(function_string)

def _update_vars(variable, value):
    # update any variables sent in by the browser
    if variable == 'var_a':
            shared_locals['var_a'] = float(value)
    elif variable == 'var_b':
            shared_locals['var_b'] = float(value)
    else:
        print('unknown variable: ', variable)

def _set_relevant_vars(to_update):
    global rel_vars, browser_weakvaldict
    # receive JS declaration of relevant variables
    rel_vars, browser_id = json.loads(to_update)
    # send variable values to browser as needed
    browser_weakvaldict[browser_id].monitor_loop = monitor_browser_vars(browser_weakvaldict[browser_id].browser)

def delete_var(v):
    del shared_locals[v]

def find_changed_vars(old_copy, new_locals):
    # input is copy of relevant variable dict and latest shared_locals; find which are changed or deleted
    changed = {}
    deleted = []
    for v in rel_vars:
        if (new_locals.get(v) == None) and (v in old_copy.keys()):
            deleted.append(v)
        elif new_locals.get(v) != old_copy.get(v):
            changed[v] = new_locals.get(v)

    return [changed, deleted]

def _update_browser_vars(browser, locals_copy):  
    # currently are not dealing with hasFocus in this way
    #browser.ExecuteJavascript("if ((document.getElementById('var_a') != document.activeElement) || !(document.hasFocus())) {document.getElementById('var_a').value = " + str(shared_locals['var_a']) + "}")
    #browser.ExecuteJavascript("if ((document.getElementById('var_b') != document.activeElement) || !(document.hasFocus())) {document.getElementById('var_b').value = " + str(shared_locals['var_b']) + "}")
    # create dictionary of the changed variables 
    changed_vars, deleted_vars = find_changed_vars(locals_copy, shared_locals)
    locals_copy.update(changed_vars)
    # handle deletions separately 
    for d in deleted_vars:
        del locals_copy[d]
    # now update the displays of any changed variables
    browser.ExecuteJavascript("update_html_variable_displays({})".format(json.dumps([changed_vars, deleted_vars])))

shared_locals = {'make_terminal': make_terminal, 'make_browser': make_browser, 'quit': sys.exit, 'delete_var':delete_var,
'var_a':1, 'var_b':42, 'num_neurons':5, 'barplot_data':[1,2,3,4,5], 'sec':h.Section(name='sec'), 'weakdict':browser_weakvaldict}

rel_vars = []

if __name__ == '__main__':
    main()
