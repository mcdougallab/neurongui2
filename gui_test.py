import gui

t = 5


def increase_t_by_one():
    global t
    t = t + 1

gui.xpanel("Hello world")
gui.xlabel("Here is some text")
gui.xvalue("h.t", "t")
gui.xbutton("Click to increase t by 1", "increase_t_by_one()")
gui.xpanel()