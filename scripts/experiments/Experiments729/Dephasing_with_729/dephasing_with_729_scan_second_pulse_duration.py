from common.abstractdevices.script_scanner.scan_methods import experiment
from excitation_blue_heat_ramsey import excitation_blue_heat_ramsey
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class scan_duration_of_second_pulse(experiment):
    
    name = 'Dephasing with 729: scan duration of second pulse'
    required_parameters = [
                           ('Dephasing','first_pulse_duration'),
                           ('Dephasing','between_pulses'),
                           ('Dephasing','scan_second_pulse_duration'),
                           
                           
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
                           
                           ('Heating','pulsing_frequency'),
                           ]

    required_parameters.extend(excitation_blue_heat_ramsey.required_parameters)
    #removing parameters we'll be overwriting, and they do not need to be loaded
    required_parameters.remove(('Excitation_729','rabi_excitation_amplitude'))
    required_parameters.remove(('Excitation_729','rabi_excitation_frequency'))
    required_parameters.remove(('Ramsey','first_pulse_duration'))
    required_parameters.remove(('Ramsey','second_pulse_duration'))
    required_parameters.remove(('Ramsey','ramsey_time'))
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation_blue_heat_ramsey)
        self.excite.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.square_pulse_generator = cxn.rigol_dg4062_server
        self.square_pulse_generator.select_device('lattice-imaging GPIB Bus - USB0::0x1AB1::0x0641::DG4D152500738')
        self.init_pulsing_freq = self.square_pulse_generator.frequency()
        self.init_pulsing_state = self.square_pulse_generator.output()
        self.square_pulse_generator.frequency(self.parameters.Heating.pulsing_frequency)
        self.square_pulse_generator.output(True)
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
        self.parameters['Ramsey.ramsey_time'] = self.parameters.Dephasing.between_pulses
        self.parameters['Ramsey.first_pulse_duration'] = self.parameters.Dephasing.first_pulse_duration
        minim,maxim,steps = self.parameters.Dephasing.scan_second_pulse_duration
        minim = minim['us']; maxim = maxim['us']
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'us') for pt in self.scan]
         
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
            self.parameters['Ramsey.second_pulse_duration'] = duration
            self.excite.set_parameters(self.parameters)
            excitation = self.excite.run(cxn, context)
            submission = [duration['us']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.data_save_context)
            self.update_progress(i)
      
    def finalize(self, cxn, context):
        self.save_parameters(self.dv, cxn, self.cxnlab, self.data_save_context)
        self.square_pulse_generator.frequency(self.init_pulsing_freq)
        self.square_pulse_generator.output(self.init_pulsing_state)
        self.excite.finalize(cxn, context)
 
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
    exprt = scan_duration_of_second_pulse(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)