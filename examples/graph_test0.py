from neuron import h

h.load_file('stdrun.hoc')

soma = h.Section(name='soma')
seg = soma(0.5)
soma.insert('hh')

ic = h.IClamp(seg)
ic.amp = 40  # since by default a very large section
ic.delay = 1
ic.dur = 1


h.xpanel("neuron")
h.xlabel("voltage graph")
g = h.Graph()
g.addvar("v", "seg.v")
g.addvar("m", "seg.hh.m")
h.xpanel()

h.finitialize(-65)

