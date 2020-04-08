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
g.addvar("v", "v(0.5)")   #hoc string example
g.addvar("m", seg.hh._ref_m)   #pointer example
#g.addvar("v", soma(0.5)._ref_v) #pointer
#g.addvar("v(0.5)")   #no label (not yet)

h.xpanel()

h.finitialize(-65)

