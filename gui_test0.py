from my_neuron import h

h.load_file('stdrun.hoc')

soma = h.Section(name='soma')
seg = soma(0.5)
soma.insert('hh')

ic = h.IClamp(seg)
ic.amp = 40  # since by default a very large section
ic.delay = 1
ic.dur = 1

is_checked = 0

h.xpanel("Hello world")
h.xlabel("Here is some text")
h.xvalue("h.t", "h.t")
h.xcheckbox("a checkbox", "is_checked")
h.xbutton("finitialize", "h.finitialize(-65)")
h.xbutton("run", "h.run()")
g = h.Graph()
g.addvar("v", "seg.v")
h.xpanel()

h.finitialize(-65)