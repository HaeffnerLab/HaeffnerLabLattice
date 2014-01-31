from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_729
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class rabi_flopping_scannable(experiment):
    
    name = 'Sit on Rabi Flop'
    trap_frequencies = [
                        ('TrapFrequencies','axial_frequency'),
                        ('TrapFrequencies','radial_frequency_1'),
                        ('TrapFrequencies','radial_frequency_2'),
                        ('TrapFrequencies','rf_drive_frequency'),                       
                        ]
    required_parameters = [
                           ('RabiFlopping','rabi_amplitude_729'),
                           ('RabiFlopping','manual_frequency_729'),
                           ('RabiFlopping','line_selection'),
                           ('RabiFlopping','rabi_amplitude_729'),
                           ('RabiFlopping','frequency_selection'),
                           ('RabiFlopping','sideband_selection'),
                           
                           ('RabiFlopping_Sit', 'sit_on_excitation'),
                           ('RabiFlopping_Sit', 'selected_ion'),
                           ('StateReadout', 'use_camera_for_readout'),
                           ]
    required_parameters.extend(trap_frequencies)
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(cls.trap_frequencies))
        parameters = parameters.union(set(excitation_729.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Excitation_729','rabi_excitation_amplitude'))
        parameters.remove(('Excitation_729','rabi_excitation_duration'))
        parameters.remove(('Excitation_729','rabi_excitation_frequency'))
        return parameters
    
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation_729)
        self.excite.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.rabi_flop_save_context = cxn.context()
    
    def setup_sequence_parameters(self):
        self.load_frequency()
        self.parameters['Excitation_729.rabi_excitation_amplitude'] = self.parameters.RabiFlopping.rabi_amplitude_729
        self.parameters['Excitation_729.rabi_excitation_duration'] = self.parameters.RabiFlopping_Sit.sit_on_excitation
    
    def load_frequency(self):
        #reloads trap frequencyies and gets the latest information from the drift tracker
        self.reload_some_parameters(self.trap_frequencies) 
        flop = self.parameters.RabiFlopping
        frequency = cm.frequency_from_line_selection(flop.frequency_selection, flop.manual_frequency_729, flop.line_selection, self.drift_tracker)
        trap = self.parameters.TrapFrequencies
        if flop.frequency_selection == 'auto':
            frequency = cm.add_sidebands(frequency, flop.sideband_selection, trap)
        self.parameters['Excitation_729.rabi_excitation_frequency'] = frequency
        
    def run(self, cxn, context):
        self.setup_sequence_parameters()
        self.load_frequency()
        self.excite.set_parameters(self.parameters)
        excitation, readouts = self.excite.run(cxn, context)
        if not self.parameters['StateReadout.use_camera_for_readout']:
            single_excitation = excitation[0]
        else:
            ion = int(self.parameters.RabiFlopping_Sit.selected_ion)
            single_excitation = excitation[ion]
        return single_excitation
     
    def finalize(self, cxn, context):
        self.excite.finalize(cxn, context)
        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = rabi_flopping_scannable(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)