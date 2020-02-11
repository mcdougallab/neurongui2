from neuron import h

a = h.Vector([1])
b = h.Vector([2])
s = h.Section(name='section1')
ell = h.List('Vector')

ell.browser()

h.xpanel('mywindow', 4, h.ref(5))

myvbox = h.VBox('Neuron')
print('myvbox.ismapped() =', myvbox.ismapped())
print('mapping...')
myvbox.map()
print('myvbox.ismapped() =', myvbox.ismapped())

h('preference = boolean_dialog("Do you prefer HOC or Python", "Python", "HOC")')
print('h.preference =', h.preference)