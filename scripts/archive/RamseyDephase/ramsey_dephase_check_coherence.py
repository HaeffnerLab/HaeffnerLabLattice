from common.abstractdevices.script_scanner.scan_methods import experiment
from excitation_ramsey_dephase_check_coherence import excitation_ramsey_dephase_check_coherence as excitation
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
import time
import labrad

class ramsey_dephase_check_coherence(experiment):
    
    name = 'RamseyDephaseCheckCoherenceTomography'
    required_parameters = [
                           ('RamseyDephaseCheckCoherence','line_selection_1'),
                           ('RamseyDephaseCheckCoherence','line_selection_2'),
                           ('RamseyDephaseCheckCoherence','sideband_selection_1'),
                           ('RamseyDephaseCheckCoherence','sideband_selection_2'),

                           ('TrapFrequencies','axial_frequency'),
                           ('TrapFrequencies','radial_frequency_1'),
                           ('TrapFrequencies','radial_frequency_2'),
                           ('TrapFrequencies','rf_drive_frequency'),
                           
                           ('Tomography','repeat_each_measurement'),
                           ('Tomography', 'line_selection'),
                           ]
    required_parameters.extend(excitation.required_parameters)
    #removing parameters we'll be overwriting, and they do not need to be loaded
    required_parameters.remove(('RamseyDephaseCheckCoherence','first_pulse_frequency'))
    required_parameters.remove(('RamseyDephaseCheckCoherence','second_pulse_frequency'))
    required_parameters.remove(('Tomography','iteration'))
    required_parameters.remove(('Tomography','tomography_excitation_frequency'))
    required_parameters.remove(('StateReadout','repeat_each_measurement'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation)
        self.excite.initialize(cxn, context, ident)
        total_iterations = 3
        self.scan = range(total_iterations)
        self.excitations = [] * total_iterations
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.data_save_context = cxn.context()
    
    def setup_sequence_parameters(self):
        deph = self.parameters.RamseyDephaseCheckCoherence
        trap = self.parameters.TrapFrequencies
        frequency_1 = cm.frequency_from_line_selection('auto', None, deph.line_selection_1, self.drift_tracker)
        frequency_1 = cm.add_sidebands(frequency_1, deph.sideband_selection_1, trap)
        self.parameters['RamseyDephaseCheckCoherence.first_pulse_frequency'] = frequency_1
        frequency_2 = cm.frequency_from_line_selection('auto', None, deph.line_selection_2, self.drift_tracker)
        frequency_2 = cm.add_sidebands(frequency_2, deph.sideband_selection_2, trap)
        self.parameters['RamseyDephaseCheckCoherence.second_pulse_frequency'] = frequency_2
        tom = self.parameters.Tomography
        frequency = cm.frequency_from_line_selection('auto', None, tom.line_selection, self.drift_tracker)
        self.parameters['Tomography.tomography_excitation_frequency'] = frequency
        
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory ,True, context = self.data_save_context)
        self.dv.new('{0} {1}'.format(self.name, datasetNameAppend),[('Iteration', 'arb')],[('Excitation Probability','Arb','Arb')], context = self.data_save_context)
        window_name = self.parameters.get('RabiTomography.window_name', ['Tomography'])
        self.dv.add_parameter('Window', window_name, context = self.data_save_context)
        self.dv.add_parameter('plotLive', True, context = self.data_save_context)
        
    def run(self, cxn, context):
        self.setup_data_vault()
        self.setup_sequence_parameters()
        for i,iteration in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            self.parameters['Tomography.iteration'] = iteration
            self.parameters['StateReadout.repeat_each_measurement'] = self.parameters.Tomography.repeat_each_measurement
            self.excite.set_parameters(self.parameters)
            excitation = self.excite.run(cxn, context)
            self.dv.add((iteration, excitation), context = self.data_save_context)
            self.excitations.append(excitation)
            self.update_progress(i)
     
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
    exprt = ramsey_dephase_check_coherence(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)