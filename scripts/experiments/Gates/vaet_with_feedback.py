from common.abstractdevices.script_scanner.scan_methods import experiment
from vaet_scan_delta import vaet_scan_delta
from vaet_scan_time import vaet_scan_time
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.CalibrationScans.fitters import peak_fitter
from labrad.units import WithUnit
from treedict import TreeDict
import time
import numpy as np
import labrad

class vaet_with_feedback(experiment):

    name = 'VAETWithFeedback'

    required_parameters = []

    # parameters to overwrite
    remove_parameters = []
        

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        #parameters = parameters.union(set(spectrum.all_required_parameters()))
        parameters = list(parameters)
        #for p in cls.remove_parameters:
        #    parameters.remove(p)
        ##will be disabling sideband cooling automatically
        #parameters.remove(('SidebandCooling','frequency_selection'))
        #parameters.remove(('SidebandCooling','manual_frequency_729'))
        #parameters.remove(('SidebandCooling','line_selection'))
        #parameters.remove(('SidebandCooling','sideband_selection'))
        #parameters.remove(('SidebandCooling','sideband_cooling_type'))
        #parameters.remove(('SidebandCooling','sideband_cooling_cycles'))
        #parameters.remove(('SidebandCooling','sideband_cooling_duration_729_increment_per_cycle'))
        #parameters.remove(('SidebandCooling','sideband_cooling_frequency_854'))
        #parameters.remove(('SidebandCooling','sideband_cooling_amplitude_854'))
        #parameters.remove(('SidebandCooling','sideband_cooling_frequency_866'))
        #parameters.remove(('SidebandCooling','sideband_cooling_amplitude_866'))
        #parameters.remove(('SidebandCooling','sideband_cooling_amplitude_729'))
        #parameters.remove(('SidebandCooling','sideband_cooling_optical_pumping_duration'))
        #parameters.remove(('SidebandCoolingContinuous','sideband_cooling_continuous_duration'))
        #parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729'))
        #parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_cycles'))
        #parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_repumps'))
        #parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_additional_866'))
        #parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_between_pulses'))
        return parameters
    
    
    def initialize(self, cxn, context, ident):

        self.ident = ident
        
        self.fitter = peak_fitter()
        self.pv = cxn.parametervault
        self.dds_cw = cxn.dds_cw
        
        self.vaet_delta = self.make_experiment(vaet_scan_delta)
        self.vaet_delta.initialize(cxn, context, self.ident)
        
        self.vaet_time = self.make_experiment(vaet_scan_time)
        self.vaet_time.initialize(cxn, context, self.ident)
        
    def run(self, cxn, context):
        
        
        ### run the vaet scan delta to find the resonance
        replace = TreeDict.fromdict({
            'VAET.window_name':['vaet_delta']})

        self.vaet_delta.set_parameters(replace)
        self.vaet_delta.set_progress_limits(0, 50.0)
        
        fr, ex = self.vaet_delta.run(cxn, context)
        
        # the order of ex is [ [SS, SD, DS, DD], [ ... ], ... ]
        fr = np.array(fr)
        ex = np.array(ex) # take only the DS measurements to fit

        ex = ex[:, 2]
        ex = ex.flatten()

        my_init_guess = np.array([ 2.333, 0.6, 1.0 ])
        vaet_freq = self.fitter.fit(fr, ex, init_guess = my_init_guess)
        vaet_freq = WithUnit(vaet_freq, 'kHz')

        self.submit_vaet_resonance(vaet_freq)

        ### now, running time dynamics
        
        ### run the vaet scan delta to find the resonance
        
        replace = TreeDict.fromdict({
            'VAET.detuning':vaet_freq})

        #print "New vaet freq: "
        #print vaet_freq

        self.vaet_time.set_parameters(replace)
        self.vaet_time.set_progress_limits(50.0, 100.0)
        
        self.vaet_time.run(cxn, context)

    def submit_vaet_resonance(self, f1):
        self.pv.set_parameter('VAET', 'detuning', f1)

    def finalize(self, cxn, context):
        self.vaet_delta.finalize(cxn, context)
        self.vaet_time.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = vaet_with_feedback(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
