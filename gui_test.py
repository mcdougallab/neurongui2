from my_neuron import h

h.load_file('stdrun.hoc')

soma = h.Section(name='soma')
seg = soma(0.5)
soma.insert('hh')

ic = h.IClamp(seg)
ic.amp = 40  # since by default a very large section
ic.delay = 1
ic.dur = 1

h.xpanel("Fancier example")

hbox = h.HBox()
hbox.intercept(True)

vbox = h.VBox()
vbox.intercept(True)

h.xlabel("Here is some text")
h.xvalue("h.t", "h.t")
h.xbutton("finitialize", "h.finitialize(-65)")
h.xbutton("run", "h.run()")

vbox.intercept(False)
vbox.map()

g = h.Graph()
g.addvar("v", "seg.v")
hbox.intercept(False)
hbox.map()

h.xpanel()

h.finitialize(-65)