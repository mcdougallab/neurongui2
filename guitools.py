from neuron import h

#
# NOTE: must make make_browser_html available in this namespace 
#

class ModelView:
    def __init__(self, dontdisplay=0):
        """Construct the ModelView object.
        
        Data is as-is at the time of creation; it is not updated dynamically.

        pass in dontdisplay=1 to not display
        """
        self._gather_data()
        if not dontdisplay:
            self._display()
    
    def _gather_data(self):
        seg_count = [sec.nseg for sec in h.allsec()]
        self.nsec = len(seg_count)
        self.nseg = sum(seg_count)
        self.celsius = h.celsius
    
    def _display(self):
        html = '''{self.nsec} sections; {self.nseg} segments<br/>{self.celsius} degrees C'''.format(self=self)
        return make_browser_html(html,
            user_mappings={},
            title='ModelView',
            size=(300, 300))        

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