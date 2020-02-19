from my_neuron import h

h.load_file('stdrun.hoc')

soma = h.Section(name='soma')
seg = soma(0.5)
soma.insert('hh')

ic = h.IClamp(seg)
ic.amp = 40  # since by default a very large section
ic.delay = 1
ic.dur = 1
is_checked = h.ref(1)

h.xpanel("Fancier example")

hbox = h.HBox()
hbox.intercept(True)

vbox = h.VBox()
vbox.intercept(True)

h.xlabel("Here is some text")
h.xvalue("h.t", "t")
h.xbutton("finitialize", "h.finitialize(-65)")
h.xbutton("run", "h.run()")
h.xstatebutton("State", is_checked)

vbox.intercept(False)
vbox.map()

#g = h.Graph()
#g.addvar("v", "seg.v")
hbox.intercept(False)
hbox.map()

h.xpanel()

h.finitialize(-65)

"""Type "help", "copyright", "credits" or "license" for more information.
>>> from neuron import h, gui
>>> h.xpanel('leprechaun')
0.0
>>> n = h.ref(0)
>>> def foo(*args):
...     return
... 
>>> h.xvalue('how many', n, False, foo, True)
0.0
>>> h.xvalue('how masdf', n, False, foo, False)
0.0
>>> h.xpanel()
0.0
>>> import warnings
>>> warnings.warn('nooooo')
__main__:1: UserWarning: nooooo
"""