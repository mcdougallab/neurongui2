import sys
import wx
from neurongui2 import run_file_after_delay, _original_program_name, app

if _original_program_name:
    if _original_program_name == '-m':
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            wx.CallLater(1, lambda: run_file_after_delay(filename))
    else:
        filename = _original_program_name
        wx.CallLater(1, lambda: run_file_after_delay(filename))

app.MainLoop()