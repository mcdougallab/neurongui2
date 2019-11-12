from neuron import h

soma = h.Section(name='soma')
soma.insert('hh')
soma.L = soma.diam = 10
ic = h.IClamp(soma(0.5))

vinit = -65
tstop = 5

def go():
    h.finitialize(vinit)
    h.continuerun(tstop)

def savedata():
    pass

mappings = {
    'seg': soma(0.5),
    'ic':ic
}

make_browser("simulation1.html",mappings)
