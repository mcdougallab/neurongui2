from neuron import h

h.load_file('stdrun.hoc')

soma = h.Section(name='soma')
seg = soma(0.5)
soma.insert('hh')

ic = h.IClamp(seg)
ic.amp = 40  # since by default a very large section
ic.delay = 1
ic.dur = 1

#is_checked = h.ref(0)
class Ref():
    def __init__(self, checked):
        self.checked = checked
is_checked = Ref(0)

def onpress():
    print("checkbox changed! as if")
    if isinstance(is_checked, Ref):
        print("value: ", is_checked.checked)
    else:
        print("value: ", is_checked[0])
    return

def onpress2():
    """print("state changed!")
    if isinstance(is_checked2, Ref):
        print("value: ", is_checked2.checked)
    else:
        print("value: ", is_checked2[0])"""
    return

def buttontest(thing1, thing2):
    print("button test worked!")
    print(thing1)
    print(thing2)
    return

is_checked2 = h.ref(0)
my_str = h.ref('yay!')

h.xpanel("Hello world")
h.xlabel("Here is some text")
h.xvalue("h.t", "t")
#h.xcheckbox("a checkbox", is_checked, "onpress()")
#h.xcheckbox("a checkbox", (is_checked, 'checked'), onpress)
#h.xstatebutton("Toggle", is_checked2, onpress2)
h.xbutton("finitialize", "finitialize(-65)")
h.xbutton("run", "run()")
#h.xbutton("test", (buttontest, ("hallo", "goodbye")))
h.xvarlabel(my_str)
#g = h.Graph()
#g.addvar("v", "seg.v")
h.xpanel()

h.finitialize(-65)