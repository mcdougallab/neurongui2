from neuron import h
import gui

h.load_file('stdrun.hoc')

soma = h.Section(name='soma')
seg = soma(0.5)
soma.insert('hh')

ic = h.IClamp(seg)
ic.amp = 40  # since by default a very large section
ic.delay = 1
ic.dur = 1

gui.xpanel("Hello world")
gui.xlabel("Here is some text")
gui.xvalue("h.t", "h.t")
gui.xbutton("finitialize", "h.finitialize(-65)")
gui.xbutton("run", "h.run()")
g = gui.Graph()
g.addvar("v", "seg.v")
gui.xpanel()

h.finitialize(-65)