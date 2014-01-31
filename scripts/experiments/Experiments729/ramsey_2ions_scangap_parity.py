from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_ramsey_2ions
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class ramsey_2ions_scangap_parity(experiment):
    
    name = 'Ramsey2ions_ScanGapParity'
    ramsey2ions_required_parameters = [
                           ('Ramsey2ions_ScanGapParity', 'scangap'),
                           ('Ramsey2ions_ScanGapParity', 'first_ion_number'),
                           ('Ramsey2ions_ScanGapParity', 'second_ion_number'),
                           ('Ramsey2ions_ScanGapParity', 'ion1_pi_over_2_line_selection'),
                           ('Ramsey2ions_ScanGapParity', 'ion1_pi_line_selection'),                         
                           ('Ramsey2ions_ScanGapParity', 'ion2_pi_over_2_line_selection'),
                           ('Ramsey2ions_ScanGapParity', 'ion2_pi_line_selection'),
 #                          ('Ramsey2ions_ScanGapParity', 'sympathetic_cooling_enable'),
                                                      
                           ]

    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.ramsey2ions_required_parameters)
        parameters = parameters.union(set(excitation_ramsey_2ions.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Ramsey_2ions','ion1_excitation_frequency1'))
        parameters.remove(('Ramsey_2ions','ion1_excitation_frequency2'))
        parameters.remove(('Ramsey_2ions','ion2_excitation_frequency1'))
        parameters.remove(('Ramsey_2ions','ion2_excitation_frequency2'))
        parameters.remove(('Ramsey_2ions','ramsey_time'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation_ramsey_2ions)
        self.excite.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.data_save_context = cxn.context()
        self.parity_save_context = cxn.context()
        self.setup_data_vault()
    
    def setup_sequence_parameters(self):
        flop = self.parameters.Ramsey2ions_ScanGapParity
        ion1_frequency1 = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), flop.ion1_pi_over_2_line_selection, self.drift_tracker)
        ion1_frequency2 = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), flop.ion1_pi_line_selection, self.drift_tracker)
        ion2_frequency1 = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), flop.ion2_pi_over_2_line_selection, self.drift_tracker)
        ion2_frequency2 = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), flop.ion2_pi_line_selection, self.drift_tracker)
        #trap = self.parameters.TrapFrequencies
        #if flop.frequency_selection == 'auto':
        #    frequency = cm.add_sidebands(frequency, flop.sideband_selection, trap)   
        #frequency += self.parameters.RamseyScanGap.detuning
        print ion1_frequency1
        self.parameters['Ramsey_2ions.ion1_excitation_frequency1'] = ion1_frequency1
        self.parameters['Ramsey_2ions.ion1_excitation_frequency2'] = ion1_frequency2
        self.parameters['Ramsey_2ions.ion2_excitation_frequency1'] = ion2_frequency1
        self.parameters['Ramsey_2ions.ion2_excitation_frequency2'] = ion2_frequency2
        #self.parameters['Excitation_729.rabi_excitation_amplitude'] = flop.rabi_amplitude_729
        #self.parameters['Ramsey.first_pulse_duration'] = self.parameters.Ramsey.rabi_pi_time / 2.0
        #self.parameters['Ramsey.second_pulse_duration'] = self.parameters.Ramsey.rabi_pi_time / 2.0
        minim,maxim,steps = self.parameters.Ramsey2ions_ScanGapParity.scangap
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
        self.dv.cd(directory, True,context = self.data_save_context)
        self.dv.cd(directory, True,context = self.parity_save_context)
        self.dv.new('{0} {1}'.format(self.name, datasetNameAppend),[('Excitation', 'us')], dependants , context = self.data_save_context)
        self.dv.new('{0} {1} Parity'.format(self.name, datasetNameAppend),[('Excitation', 'us')], [('Parity','Parity','Probability')] , context = self.parity_save_context)
        window_name = self.parameters.get('RamseyScanGap.window_name', ['Ramsey Gap Scan'])
        self.dv.add_parameter('Window', window_name, context = self.data_save_context)
        self.dv.add_parameter('plotLive', True, context = self.data_save_context)
        self.dv.add_parameter('Window', window_name, context = self.parity_save_context)
        self.dv.add_parameter('plotLive', True, context = self.parity_save_context)
        
    def run(self, cxn, context):
        self.setup_sequence_parameters()
        for i,duration in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            self.parameters['Ramsey_2ions.ramsey_time'] = duration
            self.excite.set_parameters(self.parameters)
            excitation,readouts = self.excite.run(cxn, context)
            position1 = int(self.parameters.Ramsey2ions_ScanGapParity.first_ion_number)
            position2 = int(self.parameters.Ramsey2ions_ScanGapParity.second_ion_number)
            parity = self.compute_parity(readouts,position1,position2)
            submission = [duration['us']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.data_save_context)
            self.dv.add([duration['us'], parity], context = self.parity_save_context)
            self.update_progress(i)
    
    def compute_parity(self, readouts,pos1,pos2):
        '''
        computes the parity of the provided readouts
        '''
        #print readouts
        correlated_readout = readouts[:,pos1]+readouts[:,pos2]
        parity = (correlated_readout % 2 == 0).mean() - (correlated_readout % 2 == 1).mean()
        return parity
     
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
    exprt = ramsey_2ions_scangap_parity(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)