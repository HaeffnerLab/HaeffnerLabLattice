from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import ramsey_with_stark
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class ramsey_global_stark(experiment):
    
    name = 'RamseyGlobalStark'

    gate_required_parameters = [
                           ('SZX','duration_scan'),
                           ('RabiFlopping','line_selection'),
                           ('SZX','frequency_selection'),
                           ('SZX', 'sideband_selection'),
                           ('SZX', 'detuning'),
                           ('SZX', 'ac_stark_shift'),
                           ('SZX', 'amp_red'),
                           ('SZX', 'amp_blue'),

                           ('Crystallization', 'auto_crystallization'),
                           ('Crystallization', 'camera_record_exposure'),
                           ('Crystallization', 'camera_threshold'),
                           ('Crystallization', 'max_attempts'),
                           ('Crystallization', 'max_duration'),
                           ('Crystallization', 'min_duration'),
                           ('Crystallization', 'pmt_record_duration'),
                           ('Crystallization', 'pmt_threshold'),
                           ('Crystallization', 'use_camera'),
                           ]

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.gate_required_parameters)
        parameters = parameters.union(set(cls.trap_frequencies))
        parameters = parameters.union(set(szx_gate.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('SZX','frequency'))
        parameters.remove(('LocalRotation','frequency'))
        parameters.remove(('StateReadout','pmt_mode'))
        return parameters           


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(szx_gate)
        self.excite.initialize(cxn, context, ident)
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.dds_cw = cxn.dds_cw # connection to the CW dds boards
        self.data_save_context = cxn.context()
    
    def load_frequency(self):
        #reloads trap frequencyies and gets the latest information from the drift tracker
        self.reload_some_parameters(self.trap_frequencies) 
        gate = self.parameters.SZX
        # set the double pass to the carrier frequency
        frequency = cm.frequency_from_line_selection('auto', WithUnit(0.0, 'MHz'), gate.line_selection, self.drift_tracker)
        self.parameters['SZX.frequency'] = frequency
        self.parameters['LocalRotation.frequency'] = frequency
        
        ## now program the CW dds boards
        # Ok so, because we are stupid the single pass AOMs all use the -1 order
        # so if we make the single pass frequency 81 MHz, we're actually driving -red-
        # of the carrier by 1 MHz. Keep that in mind until we change it.
        mode = gate.sideband_selection
        trap_frequency = self.parameters['TrapFrequencies.' + mode]
        
        f_local = WithUnit(80.0, 'MHz') - WithUnit(0.2, 'MHz')
        freq_blue = f_local - trap_frequency/2. - gate.detuning + gate.ac_stark_shift
        freq_red = f_local + trap_frequency/2. + gate.ac_stark_shift
        amp = WithUnit(-15., 'dBm')
        amp_blue = self.parameters.SZX.amp_blue
        amp_red = self.parameters.SZX.amp_red
        self.dds_cw.frequency('3', freq_blue)
        self.dds_cw.frequency('4', freq_red)
        self.dds_cw.frequency('5', f_local) # for driving the carrier
        self.dds_cw.amplitude('3', amp_blue)
        self.dds_cw.amplitude('4', amp_red)
        self.dds_cw.amplitude('5', amp)
        self.dds_cw.output('3', True)
        self.dds_cw.output('4', True)
        self.dds_cw.output('5', True)
        time.sleep(0.5) # just make sure everything is programmed before starting the sequence

    def run(self, cxn, context):
        self.load_frequency()
        self.parameters['StateReadout.pmt_mode'] = 'simple'
        self.excite.set_parameters(self.parameters)
        exc, readouts = self.excite.run(cxn, context)
        return exc
     
    def finalize(self, cxn, context):
        self.excite.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = szx(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
