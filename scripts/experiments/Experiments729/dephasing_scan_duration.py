from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_dephase
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class dephase_scan_duration(experiment):
    
    name = 'Dephase Scan Duration'
    dephasing_required_parameters = [
                           ('Dephasing_Pulses', 'preparation_line_selection'),
                           ('Dephasing_Pulses', 'evolution_line_selection'),
                           ('Dephasing_Pulses','preparation_sideband_selection'),
                           ('Dephasing_Pulses','evolution_sideband_selection'),
                           ('Dephasing_Pulses', 'scan_interaction_duration'),

                           ('TrapFrequencies','axial_frequency'),
                           ('TrapFrequencies','radial_frequency_1'),
                           ('TrapFrequencies','radial_frequency_2'),
                           ('TrapFrequencies','rf_drive_frequency'),
                           ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.dephasing_required_parameters)
        parameters = parameters.union(set(excitation_dephase.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Dephasing_Pulses','evolution_ramsey_time'))
        parameters.remove(('Dephasing_Pulses','evolution_pulses_frequency'))
        parameters.remove(('Dephasing_Pulses','preparation_pulse_frequency'))
        return parameters
        
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation_dephase)
        self.excite.initialize(cxn, context, ident)
        self.scan = []
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.data_save_context = cxn.context()
        self.setup_data_vault()
    
    def setup_sequence_parameters(self):
        p = self.parameters.Dephasing_Pulses
        trap = self.parameters.TrapFrequencies
        prep_line_frequency = cm.frequency_from_line_selection('auto', None, p.preparation_line_selection, self.drift_tracker)
        frequency_preparation = cm.add_sidebands(prep_line_frequency, p.preparation_sideband_selection, trap)
        #if same line is selected, match the frequency exactly
        same_line = p.preparation_line_selection == p.evolution_line_selection
        same_sideband = p.preparation_sideband_selection.aslist == p.evolution_sideband_selection.aslist
        print 'same line', same_line
        print 'same sideband', same_sideband
        if same_line and same_sideband:
            frequency_evolution = frequency_preparation
        else:
            evo_line_frequency = cm.frequency_from_line_selection('auto', None, p.evolution_line_selection, self.drift_tracker)
            frequency_evolution = cm.add_sidebands(evo_line_frequency, p.evolution_sideband_selection, trap)
        self.parameters['Dephasing_Pulses.preparation_pulse_frequency'] = frequency_preparation
        self.parameters['Dephasing_Pulses.evolution_pulses_frequency'] = frequency_evolution
        self.max_second_pulse = p.evolution_pulses_duration
        minim,maxim,steps = self.parameters.Dephasing_Pulses.scan_interaction_duration
        minim = minim['us']; maxim = maxim['us']
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'us') for pt in self.scan]
        
    def setup_data_vault(self):
        localtime = time.localtime()
        dirappend = [time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory, True,context = self.data_save_context)
        
    def data_vault_new_trace(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        output_size = self.excite.output_size
        dependants = [('Excitation','Ion {}'.format(ion),'Probability') for ion in range(output_size)]
        self.dv.new('{0} {1}'.format(self.name, datasetNameAppend),[('Excitation', 'us')], dependants , context = self.data_save_context)
        window_name = ['Dephasing, Scan Duration']
        self.dv.add_parameter('Window', window_name, context = self.data_save_context)
        self.dv.add_parameter('plotLive', True, context = self.data_save_context)
        
    def run(self, cxn, context):
        p = self.parameters.Dephasing_Pulses
        self.data_vault_new_trace()
        self.setup_sequence_parameters()
        for i,interaction_duration in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop:
                return False
            second_pulse_dur = min(self.max_second_pulse, interaction_duration)
            ramsey_time = max(WithUnit(0,'us'), interaction_duration - self.max_second_pulse)
            p.evolution_ramsey_time = ramsey_time
            p.evolution_pulses_duration = second_pulse_dur
            self.excite.set_parameters(self.parameters)
            excitation, readout = self.excite.run(cxn, context)
            submission = [interaction_duration['us']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.data_save_context)
            self.update_progress(i)
        self.save_parameters(self.dv, cxn, self.cxnlab, self.data_save_context)
        return True
     
    def finalize(self, cxn, context):
        pass

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
    exprt = dephase_scan_duration(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)