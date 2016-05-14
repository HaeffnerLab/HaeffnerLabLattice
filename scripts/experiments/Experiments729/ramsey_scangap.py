from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_ramsey
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
import lattice.scripts.scriptLibrary.scan_methods as sm
from lattice.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class ramsey_scangap(experiment):
    
    name = 'RamseyScanGap'
    ramsey_required_parameters = [
                           ('RamseyScanGap', 'detuning'),
                           ('RamseyScanGap', 'scangap'),
                           
                           ('RabiFlopping','rabi_amplitude_729'),
                           ('RabiFlopping','manual_frequency_729'),
                           ('RabiFlopping','line_selection'),
                           ('RabiFlopping','rabi_amplitude_729'),
                           ('RabiFlopping','frequency_selection'),
                           ('RabiFlopping','sideband_selection'),
                           
                           ('TrapFrequencies','axial_frequency'),
                           ('TrapFrequencies','radial_frequency_1'),
                           ('TrapFrequencies','radial_frequency_2'),
                           ('TrapFrequencies','rf_drive_frequency'),
                           ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.ramsey_required_parameters)
        parameters = parameters.union(set(excitation_ramsey.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Excitation_729','rabi_excitation_amplitude'))
        parameters.remove(('Excitation_729','rabi_excitation_frequency'))
        parameters.remove(('Ramsey','ramsey_time'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation_ramsey)
        self.excite.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.save_context = cxn.context()     
        try:
            self.grapher = cxn.grapher
        except: self.grapher = None
        self.cxn = cxn
        
        self.setup_sequence_parameters()     
        self.setup_data_vault()
    
    def setup_sequence_parameters(self):
        flop = self.parameters.RabiFlopping
        trap = self.parameters.TrapFrequencies
        if flop.frequency_selection == 'auto':
            frequency = sm.compute_frequency_729(flop.line_selection, flop.sideband_selection, trap, self.drift_tracker)
        else:
            frequency = flop.manual_frequency_729
        frequency += self.parameters.RamseyScanGap.detuning
        #print frequency
        self.parameters['Excitation_729.rabi_excitation_frequency'] = frequency
        self.parameters['Excitation_729.rabi_excitation_amplitude'] = flop.rabi_amplitude_729
        self.scan = sm.simple_scan(self.parameters.RamseyScanGap.scangap, 'us')
        
    def run(self, cxn, context):

        dv_args = {
            'pulse_sequence': 'ramsey',
            'parameter':'Ramsey.ramsey_time',
            'headings': ['Ion {}'.format(ion) for ion in range(self.excite.output_size)],
            'window_name':'ramsey',
            'axis': self.scan,
            }
        sm.setup_data_vault(cxn, self.save_context, dv_args)
   

        self.setup_sequence_parameters()
        for i,duration in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            self.parameters['Ramsey.ramsey_time'] = duration
            self.excite.set_parameters(self.parameters)
            excitation, readouts = self.excite.run(cxn, context)
            submission = [duration['us']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)
     
    def finalize(self, cxn, context):
        #self.save_parameters(self.dv, cxn, self.cxnlab, self.data_save_context)
        pass
    
    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)

    def save_parameters(self, dv, cxn, context):
        measuredDict = dvParameters.measureParameters(cxn)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)   

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ramsey_scangap(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
