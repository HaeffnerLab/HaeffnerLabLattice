from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_ramsey
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class ramsey_scanphase(experiment):
    
    name = 'RamseyScanPhase'
    required_parameters = [
                           ('RamseyScanPhase', 'scanphase'),
                           
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
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(excitation_ramsey.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Excitation_729','rabi_excitation_amplitude'))
        parameters.remove(('Excitation_729','rabi_excitation_frequency'))
        parameters.remove(('Ramsey','second_pulse_phase'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation_ramsey)
        self.excite.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.data_save_context = cxn.context()
        self.setup_data_vault()
    
    def setup_sequence_parameters(self):
        flop = self.parameters.RabiFlopping
        frequency = cm.frequency_from_line_selection(flop.frequency_selection, flop.manual_frequency_729, flop.line_selection, self.drift_tracker)
        trap = self.parameters.TrapFrequencies
        if flop.frequency_selection == 'auto':
            frequency = cm.add_sidebands(frequency, flop.sideband_selection, trap)   
        self.parameters['Excitation_729.rabi_excitation_frequency'] = frequency
        self.parameters['Excitation_729.rabi_excitation_amplitude'] = flop.rabi_amplitude_729
        self.parameters['Ramsey.first_pulse_duration'] = self.parameters.Ramsey.rabi_pi_time / 2.0
        self.parameters['Ramsey.second_pulse_duration'] = self.parameters.Ramsey.rabi_pi_time / 2.0
        minim,maxim,steps = self.parameters.RamseyScanPhase.scanphase
        minim = minim['deg']; maxim = maxim['deg']
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'deg') for pt in self.scan]
        
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        output_size = self.excite.output_size
        dependants = [('Excitation','Ion {}'.format(ion),'Probability') for ion in range(output_size)]
        self.dv.new('{0} {1}'.format(self.name, datasetNameAppend),[('Second pulse phase', 'deg')], dependants , context = self.data_save_context)
        window_name = self.parameters.get('RamseyScanPhase.window_name', ['Ramsey Phase Scan'])
        self.dv.add_parameter('Window', window_name, context = self.data_save_context)
        self.dv.add_parameter('plotLive', True, context = self.data_save_context)
        
    def run(self, cxn, context):
        self.setup_sequence_parameters()
        for i,duration in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            self.parameters['Ramsey.second_pulse_phase'] = duration
            self.excite.set_parameters(self.parameters)
            excitation, readouts = self.excite.run(cxn, context)
            submission = [duration['deg']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.data_save_context)
            self.update_progress(i)
            
    @property
    def output_size(self):
        if self.use_camera:
            return int(self.parameters.IonsOnCamera.ion_number)
        else:
            return 1
     
    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.data_save_context)

    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)

    def save_parameters(self, dv, cxn, cxnlab, context):
        measuredDict = dvParameters.measureParameters(cxn, cxnlab)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)   

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ramsey_scanphase(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)