from neuron import h, window
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
h.load_file('stdrun.hoc')

soma = h.Section(name='soma')
soma.L = soma.diam = 10
soma.insert('hh')

ic = h.IClamp(soma(0.5))
ic.amp = 1
ic.delay = 1
ic.dur = 0.1

t = h.Vector().record(h._ref_t)
v = h.Vector().record(soma(0.5)._ref_v)

h.finitialize(-65)
h.continuerun(5)

plot = figure()
plot.line(t, v, line_width=2)

plot2 = figure()
x = h.Vector(range(10))
plot2.line(x, x*x, line_width=3, line_color='red')

html = """
    <style>body {{background-color: white}}</style>
    <h1><span style="color:blue">Hello</span> everybody</h1>
    Press the button to toggle the graphs (actually: a new one is drawn each time).<br/>
    <button data-onclick="go">Press me</button><br/><br/><br/>
    <div id="myplot">{}</div>
""".format(file_html(plot, CDN, ""))

count_press = 0
def go():
    global count_press
    count_press += 1
    if count_press % 2:
        w.update_html("#myplot", file_html(plot2, CDN, ""))
    else:
        w.update_html("#myplot", file_html(plot, CDN, ""))

w = window(html,
           {'go': go},
           title='Bokeh Demo')


