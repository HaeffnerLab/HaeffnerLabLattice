from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_ramsey_2ions
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace
import numpy as np

class Parity_LLI_scan_gap(experiment):
    
    name = 'Parity_LLI_scan_gap'
    Parity_LLI_required_parameters = [
                           ('Parity_LLI', 'scangap'),
                           ('Parity_LLI', 'mirror_state'),
                           ('Parity_transitions', 'left_ion_number'),
                           ('Parity_transitions', 'right_ion_number'),
                           ('Parity_transitions', 'left_ionSp12Dp12_pi_time'),
                           ('Parity_transitions', 'left_ionSp12Dp12_power'),
                           ('Parity_transitions', 'left_ionSm12Dm12_pi_time'),
                           ('Parity_transitions', 'left_ionSm12Dm12_power'),
                           ('Parity_transitions', 'left_ionSp12Dp52_pi_time'),
                           ('Parity_transitions', 'left_ionSp12Dp52_power'),
                           ('Parity_transitions', 'left_ionSm12Dm52_pi_time'),
                           ('Parity_transitions', 'left_ionSm12Dm52_power'),
                           
                           ('Parity_transitions', 'right_ionSp12Dp12_pi_time'),
                           ('Parity_transitions', 'right_ionSp12Dp12_power'),
                           ('Parity_transitions', 'right_ionSm12Dm12_pi_time'),
                           ('Parity_transitions', 'right_ionSm12Dm12_power'),
                           ('Parity_transitions', 'right_ionSp12Dp52_pi_time'),
                           ('Parity_transitions', 'right_ionSp12Dp52_power'),
                           ('Parity_transitions', 'right_ionSm12Dm52_pi_time'),
                           ('Parity_transitions', 'right_ionSm12Dm52_power'),
                             
                           ('StateReadout', 'parity_threshold_low'),
                           ('StateReadout', 'parity_threshold_high'),       
                           ('StateReadout', 'use_camera_for_readout'),     
                             
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
        
        parameters = set(cls.Parity_LLI_required_parameters)
        parameters = parameters.union(set(excitation_ramsey_2ions.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Ramsey_2ions','ion1_excitation_frequency1'))
        parameters.remove(('Ramsey_2ions','ion1_excitation_frequency2'))
        parameters.remove(('Ramsey_2ions','ion2_excitation_frequency1'))
        parameters.remove(('Ramsey_2ions','ion2_excitation_frequency2'))
        parameters.remove(('Ramsey_2ions','ion1_excitation_amplitude1'))
        parameters.remove(('Ramsey_2ions','ion1_excitation_amplitude2'))
        parameters.remove(('Ramsey_2ions','ion2_excitation_amplitude1'))
        parameters.remove(('Ramsey_2ions','ion2_excitation_amplitude2'))
        parameters.remove(('Ramsey_2ions','ion1_excitation_duration1'))
        parameters.remove(('Ramsey_2ions','ion1_excitation_duration2'))
        parameters.remove(('Ramsey_2ions','ion2_excitation_duration1'))
        parameters.remove(('Ramsey_2ions','ion2_excitation_duration2'))
        parameters.remove(('Ramsey_2ions','ramsey_time'))
        
        
        parameters.remove(('OpticalPumping','line_selection'))
        parameters.remove(('OpticalPumpingAux','aux_op_line_selection'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.scan = []
        self.amplitude = None
        self.duration = None
        #self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.data_save_context = cxn.context()
        self.parity_save_context = cxn.context()
        
        ##############
        self.excite = self.make_experiment(excitation_ramsey_2ions)
        self.setup_sequence_parameters()
        self.excite.set_parameters(self.parameters)
        self.excite.initialize(cxn, context, ident)
        ##############
        
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
        self.setup_data_vault()
        
    def update_mirror_state(self):
        self.setup_sequence_parameters()
        self.excite.set_parameters(self.parameters)
        self.excite.setup_sequence_parameters()
    
    def setup_sequence_parameters(self):
        
        if self.parameters.Parity_LLI.mirror_state == True:
            self.parameters['Ramsey_2ions.ion1_excitation_frequency1'] = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), 'S-1/2D-1/2', self.drift_tracker)
            self.parameters['Ramsey_2ions.ion1_excitation_frequency2'] = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), 'S-1/2D-5/2', self.drift_tracker)
            self.parameters['Ramsey_2ions.ion2_excitation_frequency1'] = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), 'S+1/2D+1/2', self.drift_tracker)
            self.parameters['Ramsey_2ions.ion2_excitation_frequency2'] = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), 'S+1/2D+5/2', self.drift_tracker)
            self.parameters['Ramsey_2ions.ion1_excitation_amplitude1'] = self.parameters['Parity_transitions.left_ionSm12Dm12_power']
            self.parameters['Ramsey_2ions.ion1_excitation_amplitude2'] = self.parameters['Parity_transitions.left_ionSm12Dm52_power']
            self.parameters['Ramsey_2ions.ion2_excitation_amplitude1'] = self.parameters['Parity_transitions.right_ionSp12Dp12_power']
            self.parameters['Ramsey_2ions.ion2_excitation_amplitude2'] = self.parameters['Parity_transitions.right_ionSp12Dp52_power']
            self.parameters['Ramsey_2ions.ion1_excitation_duration1'] = self.parameters['Parity_transitions.left_ionSm12Dm12_pi_time']/2.0
            self.parameters['Ramsey_2ions.ion1_excitation_duration2'] = self.parameters['Parity_transitions.left_ionSm12Dm52_pi_time']
            self.parameters['Ramsey_2ions.ion2_excitation_duration1'] = self.parameters['Parity_transitions.right_ionSp12Dp12_pi_time']/2.0
            self.parameters['Ramsey_2ions.ion2_excitation_duration2'] = self.parameters['Parity_transitions.right_ionSp12Dp52_pi_time']
            self.parameters['OpticalPumping.line_selection'] = 'S+1/2D-3/2'
            self.parameters['OpticalPumpingAux.aux_op_line_selection'] = 'S-1/2D+3/2'
        else:
            self.parameters['Ramsey_2ions.ion1_excitation_frequency1'] = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), 'S+1/2D+1/2', self.drift_tracker)
            self.parameters['Ramsey_2ions.ion1_excitation_frequency2'] = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), 'S+1/2D+5/2', self.drift_tracker)
            self.parameters['Ramsey_2ions.ion2_excitation_frequency1'] = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), 'S-1/2D-1/2', self.drift_tracker)
            self.parameters['Ramsey_2ions.ion2_excitation_frequency2'] = cm.frequency_from_line_selection('auto', WithUnit(0.00, 'MHz'), 'S-1/2D-5/2', self.drift_tracker)
            self.parameters['Ramsey_2ions.ion1_excitation_amplitude1'] = self.parameters['Parity_transitions.left_ionSp12Dp12_power']
            self.parameters['Ramsey_2ions.ion1_excitation_amplitude2'] = self.parameters['Parity_transitions.left_ionSp12Dp52_power']
            self.parameters['Ramsey_2ions.ion2_excitation_amplitude1'] = self.parameters['Parity_transitions.right_ionSm12Dm12_power']
            self.parameters['Ramsey_2ions.ion2_excitation_amplitude2'] = self.parameters['Parity_transitions.right_ionSm12Dm52_power']
            self.parameters['Ramsey_2ions.ion1_excitation_duration1'] = self.parameters['Parity_transitions.left_ionSp12Dp12_pi_time']/2.0
            self.parameters['Ramsey_2ions.ion1_excitation_duration2'] = self.parameters['Parity_transitions.left_ionSp12Dp52_pi_time']
            self.parameters['Ramsey_2ions.ion2_excitation_duration1'] = self.parameters['Parity_transitions.right_ionSm12Dm12_pi_time']/2.0
            self.parameters['Ramsey_2ions.ion2_excitation_duration2'] = self.parameters['Parity_transitions.right_ionSm12Dm52_pi_time']
            self.parameters['OpticalPumping.line_selection'] = 'S-1/2D+3/2'
            self.parameters['OpticalPumpingAux.aux_op_line_selection'] = 'S+1/2D-3/2'
            
        
        minim,maxim,steps = self.parameters.Parity_LLI.scangap
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
        #self.setup_sequence_parameters()
        for i,duration in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            
            excitation, readouts = self.get_excitation_crystallizing(cxn, context, duration) 

            ### pmt or camera readout ###
            if self.parameters.StateReadout.use_camera_for_readout:
                position1 = int(self.parameters.Parity_transitions.left_ion_number)
                position2 = int(self.parameters.Parity_transitions.right_ion_number)
                parity = self.compute_parity(readouts,position1,position2)
            else:
                threshold_low = self.parameters.StateReadout.parity_threshold_low
                threshold_high = self.parameters.StateReadout.parity_threshold_high
                parity = self.compute_parity_pmt(readouts,threshold_low,threshold_high)

            submission = [duration['us']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.data_save_context)
            self.dv.add([duration['us'], parity], context = self.parity_save_context)
            self.update_progress(i)
            
    def get_excitation_crystallizing(self, cxn, context, duration):
        self.setup_sequence_parameters()
        self.parameters['Ramsey_2ions.ramsey_time'] = duration
        self.excite.set_parameters(self.parameters)
        self.update_mirror_state()
        excitation,readouts = self.excite.run(cxn, context)
        if self.parameters.Crystallization.auto_crystallization:
            initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
            #if initially melted, redo the point
            while initally_melted:
                if not got_crystallized:
                    #if crystallizer wasn't able to crystallize, then pause and wait for user interaction
                    self.cxn.scriptscanner.pause_script(self.ident, True)
                    should_stop = self.pause_or_stop()
                    if should_stop: return None
                excitation,readouts = self.excite.run(cxn, context)
                initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
        return excitation, readouts
    
    def compute_parity(self, readouts,pos1,pos2):
        '''
        computes the parity of the provided readouts
        '''
        #print readouts
        correlated_readout = readouts[:,pos1]+readouts[:,pos2]
        parity = (correlated_readout % 2 == 0).mean() - (correlated_readout % 2 == 1).mean()
        return parity
    
    def compute_parity_pmt(self, readouts,threshold_low,threshold_high):
        '''
        computes the parity of the provided readouts using a pmt
        '''
        even_parity = np.count_nonzero((readouts <= threshold_low)|(readouts >= threshold_high))
        print "even = ", even_parity
        odd_parity  = np.count_nonzero((readouts >= threshold_low)&(readouts <= threshold_high))
        print "odd = ", odd_parity
        parity = (even_parity - odd_parity)/float(len(readouts))
        return parity
     
    def finalize(self, cxn, context):
        pass
        #self.save_parameters(self.dv, cxn, self.cxnlab, self.data_save_context)

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
    exprt = Parity_LLI_scan_gap(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)