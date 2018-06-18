from PyQt4 import QtGui, uic
import os
from common.clients.connection import connection
from twisted.internet.defer import inlineCallbacks
import threading
import subprocess


basepath =  os.path.dirname(__file__)
path = os.path.join(basepath, "quick_actions.ui")
base, form = uic.loadUiType(path)

class widget_ui(base, form):
    def __init__(self, parent = None):
        super(widget_ui, self).__init__(parent)
        self.isloading = False
        self.setupUi(self)

class actions_widget(QtGui.QFrame, widget_ui):
    def __init__(self,reactor,cxn = None, parent=None):
        self.reactor = reactor
        self.cxn = cxn
        QtGui.QDialog.__init__(self)
        widget_ui.__init__(self)
        self.connect()
    
    @inlineCallbacks
    def connect(self):
        from labrad.units import WithUnit
        from labrad.types import Error
        self.WithUnit = WithUnit
        self.Error = Error
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            self.connect_layout()
        except Exception, e:
            print e
            self.setDisabled(True)
    
    def connect_layout(self):
        self.Load_ion.pressed.connect(self.ion_loader)
        self.crystallize.pressed.connect(self.on_crystallize)
        self.fromdc.pressed.connect(self.on_from_dc)
        self.fromstate.pressed.connect(self.on_from_state)
        self.todc.pressed.connect(self.on_to_dc)
        self.tostate.pressed.connect(self.on_to_state)
    
    @inlineCallbacks
    def ion_loader(self):
        script = "/home/lattice/LabRAD/lattice/clients/automation_functions/load_single_ion.py"

        def run_loading():
            self.p = subprocess.Popen(["python", "/home/lattice/LabRAD/lattice/clients/automation_functions/load_single_ion.py"])
            self.isloading = True
            self.p.wait()
            self.isloading = False
            self.Load_ion.setText("Load ion")
            return

        if self.isloading:         
            self.p.kill()
            del self.p
            self.Load_ion.setText("Load_ion")
            os.system("python /home/lattice/LabRAD/lattice/clients/automation_functions/load_single_ion.py 1")       
            #cxn.pulser.switch_manual('bluePI', False)
            print "Terminating load_single_ion.py"
        
        else:
            print "Running load_single_ion.py"
            thread = threading.Thread(target=run_loading, args=())
            thread.start()
            self.Load_ion.setText("stop_loading")
            #execfile(script)
            yield 1
        

    @inlineCallbacks
    def on_crystallize(self):
        xtal = yield self.cxn.get_server('Crystallizer')
        yield xtal.crystallize_once()
    
    @inlineCallbacks
    def on_to_state(self):
        pv = yield self.cxn.get_server('scriptscanner')
        pulser = yield self.cxn.get_server('Pulser')
        ampl397 = yield pulser.amplitude('global397')
        # ampl866 = yield pulser.amplitude('866DP')
        freq397 = yield pulser.frequency('global397')
        # freq866 = yield pulser.frequency('866DP')
        yield pv.set_parameter('StateReadout','state_readout_amplitude_397', ampl397)
        # yield pv.set_parameter('StateReadout','state_readout_amplitude_866',ampl866)
        yield pv.set_parameter('StateReadout','state_readout_frequency_397',freq397)
        # yield pv.set_parameter('StateReadout','state_readout_frequency_866',freq866)
    
    @inlineCallbacks
    def on_to_dc(self):
        pv = yield self.cxn.get_server('scriptscanner')
        pulser = yield self.cxn.get_server('Pulser')
        ampl397 = yield pulser.amplitude('global397')
        # ampl866 = yield pulser.amplitude('866DP')
        freq397 = yield pulser.frequency('global397')
        # freq866 = yield pulser.frequency('866DP')
        yield pv.set_parameter('DopplerCooling','doppler_cooling_amplitude_397',ampl397)
        # yield pv.set_parameter('DopplerCooling','doppler_cooling_amplitude_866',ampl866)
        yield pv.set_parameter('DopplerCooling','doppler_cooling_frequency_397',freq397)
        # yield pv.set_parameter('DopplerCooling','doppler_cooling_frequency_866',freq866)
        
    @inlineCallbacks
    def on_from_dc(self):
        pv = yield self.cxn.get_server('scriptscanner')
        pulser = yield self.cxn.get_server('Pulser')
        ampl397 = yield pv.get_parameter(('DopplerCooling','doppler_cooling_amplitude_397'))
        # ampl866 = yield pv.get_parameter(('DopplerCooling','doppler_cooling_amplitude_866'))
        freq397 = yield pv.get_parameter(('DopplerCooling','doppler_cooling_frequency_397'))
        # freq866 = yield pv.get_parameter(('DopplerCooling','doppler_cooling_frequency_866'))
        # yield pulser.frequency('866DP', freq866)
        # yield pulser.amplitude('866DP', ampl866)
        yield pulser.frequency('global397', freq397)
        yield pulser.amplitude('global397', ampl397)
    
    @inlineCallbacks
    def on_from_state(self):
        pv = yield self.cxn.get_server('scriptscanner')
        pulser = yield self.cxn.get_server('Pulser')
        ampl397 = yield pv.get_parameter(('StateReadout','state_readout_amplitude_397'))
        ampl866 = yield pv.get_parameter(('StateReadout','state_readout_amplitude_866'))
        freq397 = yield pv.get_parameter(('StateReadout','state_readout_frequency_397'))
        freq866 = yield pv.get_parameter(('StateReadout','state_readout_frequency_866'))
        # yield pulser.frequency('866DP', freq866)
        # yield pulser.amplitude('866DP', ampl866)
        yield pulser.frequency('global397', freq397)
        yield pulser.amplitude('global397', ampl397)
    
    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None
    
    def closeEvent(self, x):
        self.reactor.stop()  
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    electrodes = actions_widget(reactor)
    electrodes.show()
    reactor.run()
