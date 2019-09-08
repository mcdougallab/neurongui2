import wx 
import wx.py.crust

_all_windows = []


def make_terminal():
    window = wx.Frame(None, title="Console [{}]".format(len(_all_windows) + 1), size=(600, 400))
    # by explicitly specifying the locals, we couple the shells together
    # while simultaneously keeping them unable to directly access our code
    # hmm... maybe a bad idea; should we transfer over a gui variable?
    shell = wx.py.shell.Shell(parent=window, locals=shared_locals)
    _all_windows.append(shell)
    shell.run("print('type make_terminal() to open another terminal')", verbose=False, prompt=False)
    window.Show(True) 

shared_locals = {'make_terminal': make_terminal}


app = wx.App() 
make_terminal()
app.MainLoop()