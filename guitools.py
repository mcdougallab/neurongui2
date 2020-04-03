from neuron import h

#
# NOTE: must make make_browser_html available in this namespace 
#

def _mv_item_to_html(item):
    children = item.children
    if children is None:
        children = []
    if not item.name.strip() and not children:
        result = '</ul><ul>'
    else:
        result = '<li>' + item.name
        if children:
            result += '\n<ul>'
            for child in children:
                result += _mv_item_to_html(child)
            result += '</ul>\n'
        result += '</li>\n'
    return result

def load_file(filename):
    import os
    h.load_file(os.path.join(h.neuronhome(), 'lib', 'hoc', filename))

class ModelView:
    def __init__(self, display=True):
        """Construct the ModelView object.
        
        Data is as-is at the time of creation; it is not updated dynamically.

        pass in display=False to not display
        """
        # TODO: note that this may cause problems if the libraries are already loaded somehow
        #       in a way that didn't specify the full path as templates cannot be redefined in 
        #       HOC

        # start by loading the libraries
        h('objref nil')
        h('begintemplate ModelViewGUI\nendtemplate ModelViewGUI')
        h('begintemplate ModelViewXML\nendtemplate ModelViewXML')
        # this next one will be a problem whenever there is a KSChan
        h('begintemplate KSTransHelper\nendtemplate KSTransHelper')
        h.load_file('stdlib.hoc')
        load_file('mview/parmsets.hoc')
        load_file('mview/treeview.hoc')
        load_file('mview/parmvals.hoc')
        load_file('mview/secanal.hoc')
        load_file('mview/ppanal.hoc')
        load_file('mview/distinct.hoc')
        load_file('mview/realcell.hoc')
        load_file('mview/artview.hoc')
        load_file('mview/ncview.hoc')
        load_file('mview/allcell.hoc')
        load_file('mview/allpp.hoc')
        load_file('mview/rcclasses.hoc')
        load_file('mview/mview1.hoc')

        self.mview = h.ModelView(0)
        self.tree = self.mview.display

        if display:
            self._display()
    
    def _to_html(self):
        result = '<ul>'
        for item in self.tree.top:
            result += _mv_item_to_html(item)
        return result + '</ul>'

    def _display(self):
        return make_browser_html(self._to_html(),
            user_mappings={},
            title='ModelView',
            size=(600, 600))        

class RunControl:
    def __init__(self):
        html = """
        <table style="width:100%">
            <tr><td><button data-onclick="init()">Init (mV)</button></td><td><input type="number" data-variable="v_init"></input></tr>
            <tr><td><button data-onclick="run()">Init & run</button></td></tr>
            <tr><td><button data-onclick="stopbutton()">Stop</button></td></tr>
            <tr><td><button data-onclick="do_continue_until()">Continue until (ms)</button></td><td><input type="number" data-variable="continue_til"></input></tr>
            <tr><td><button data-onclick="do_continue_for()">Continue for (ms)</button></td><td><input type="number" data-variable="continue_for"></input></tr>
            <tr><td><button data-onclick="fadvance()">Single Step</button></td></tr>
            <tr><td>t (ms)</td><td><input type="number" data-variable="t"></input></tr>
            <tr><td>tstop (ms)</td><td><input type="number" data-variable="tstop"></input></tr>
            <tr><td>dt (ms)</td><td><input type="number" data-variable="dt"></input></tr>
            <tr><td>Real Time (s)</td><td><input type="number" data-variable="realtime" disabled></input></tr>
        </table>
        """
        self.my_continue_til = h.ref(5)
        self.my_continue_for = h.ref(1)
        user_mappings = {
            'v_init': h._ref_v_init,
            'continue_til': self.my_continue_til,
            'continue_for': self.my_continue_for,
            't': h._ref_t,
            'tstop': h._ref_tstop,
            'dt': h._ref_dt,
            'run()': h.run,
            'init()': h.stdinit,
            'fadvance()': h.fadvance,
            'realtime': h._ref_realtime,
            'stopbutton()': self.stop,
            'do_continue_until()': lambda: h.continuerun(self.my_continue_til[0]),
            'do_continue_for()': lambda: h.continuerun(h.t + self.my_continue_for[0])
        }
        self._frame = make_browser_html(html,
            user_mappings=user_mappings,
            title='Run Control',
            size=(280, 400))
    
    def stop(self):
        h.stoprun = True