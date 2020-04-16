import neurongui2
from neuron import h, window

html = """
    <h1><span style="color:blue">Hello</span> everybody</h1>
    <input type="number" data-variable="t">
    <label>time (<i>ms</i>)</label><br/>
    The variable s: <span data-variable="s"></span><br/><br/>
    <button data-onclick="go">Press me</button>
"""

h('strdef s')

h.s = 'Hello'

def go():
    print(f'You pressed the button! h.t = {h.t}')

w = window(html,
           {'t': h._ref_t, 'go': go, 's': h._ref_s},
           title='Demo')

h.s = 'Goodbye'


