from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_ramsey_2ions
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
#from numpy import linspace
import numpy as np
import datetime

class Parity_LLI_phase_tracker(experiment):
    
    name = 'Parity_LLI_phase_tracker'
    Parity_LLI_required_parameters = [
                           ('Parity_LLI', 'mirror_state'),
                           ('Parity_LLI', 'short_ramsey_time'),
                           ('Parity_LLI', 'long_ramsey_time'),
                           ('Parity_LLI', 'phase_feedback'),
                           ('Parity_LLI', 'phase_mirror_state'),
                           ('Parity_LLI', 'phase_no_mirror_state'),
                           ('Parity_LLI', 'phase_mirror_state_short_time'),
                           ('Parity_LLI', 'phase_no_mirror_state_short_time'),
                           ('Parity_LLI', 'use_short_ramsey_time'),
                           ('Parity_LLI', 'contrast'),

        
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
                           
                           ('Ramsey_2ions','ion2_excitation_phase1'), 
                           
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
        parameters.remove(('Ramsey_2ions','ion2_excitation_phase1'))
        
        #parameters.remove(('Parity_LLI','scangap'))
        
        parameters.remove(('OpticalPumping','line_selection'))
        parameters.remove(('OpticalPumpingAux','aux_op_line_selection'))
        
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.pv = cxn.parametervault
        self.save_data = cxn.context()
        ##############
        self.excite = self.make_experiment(excitation_ramsey_2ions)
        self.excite.set_parameters(self.parameters)
        self.excite.initialize(cxn, context, ident)
        ##############
        
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
        self.setup_data_vault()
        
    def update_mirror_state(self, phase_plus_pi):
        self.setup_sequence_parameters(phase_plus_pi)
        self.excite.set_parameters(self.parameters)
        self.excite.setup_sequence_parameters()
        
        
    def setup_sequence_parameters(self, phase_plus_pi):
        ### reload the phase ###
        self.reload_some_parameters([('Parity_LLI', 'phase_mirror_state'),
                                     ('Parity_LLI', 'phase_mirror_state_short_time'),
                                     ('Parity_LLI', 'phase_no_mirror_state_short_time'),
                                     ('Parity_LLI', 'phase_no_mirror_state'),])
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
            if self.parameters.Parity_LLI.use_short_ramsey_time:
                self.parameters['Ramsey_2ions.ramsey_time'] = self.parameters['Parity_LLI.short_ramsey_time']
                if phase_plus_pi:
                    self.parameters['Ramsey_2ions.ion2_excitation_phase1'] = self.parameters['Parity_LLI.phase_mirror_state_short_time']+WithUnit(180.0,'deg')
                else:
                    self.parameters['Ramsey_2ions.ion2_excitation_phase1'] = self.parameters['Parity_LLI.phase_mirror_state_short_time']
            else:
                self.parameters['Ramsey_2ions.ramsey_time'] = self.parameters['Parity_LLI.long_ramsey_time']
                if phase_plus_pi:
                    self.parameters['Ramsey_2ions.ion2_excitation_phase1'] = self.parameters['Parity_LLI.phase_mirror_state']+WithUnit(180.0,'deg')
                else:
                    self.parameters['Ramsey_2ions.ion2_excitation_phase1'] = self.parameters['Parity_LLI.phase_mirror_state']
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
            if self.parameters.Parity_LLI.use_short_ramsey_time:
                self.parameters['Ramsey_2ions.ramsey_time'] = self.parameters['Parity_LLI.short_ramsey_time']
                if phase_plus_pi:
                    self.parameters['Ramsey_2ions.ion2_excitation_phase1'] = self.parameters['Parity_LLI.phase_no_mirror_state_short_time']+WithUnit(180.0,'deg')
                else:
                    self.parameters['Ramsey_2ions.ion2_excitation_phase1'] = self.parameters['Parity_LLI.phase_no_mirror_state_short_time']
            else:
                self.parameters['Ramsey_2ions.ramsey_time'] = self.parameters['Parity_LLI.long_ramsey_time']
                if phase_plus_pi:
                    self.parameters['Ramsey_2ions.ion2_excitation_phase1'] = self.parameters['Parity_LLI.phase_no_mirror_state']+WithUnit(180.0,'deg')
                else:
                    self.parameters['Ramsey_2ions.ion2_excitation_phase1'] = self.parameters['Parity_LLI.phase_no_mirror_state']
        
        
    def setup_data_vault(self):
        localtime = time.localtime()
        directory_LLI = ['','Drift_Tracking','LLI_tracking_phase_parity']
        directory_LLI.append(time.strftime("%Y%b%d",localtime))
        self.dv.cd(directory_LLI ,True, context = self.save_data)
        if self.parameters.Parity_LLI.use_short_ramsey_time:
            if self.parameters.Parity_LLI.mirror_state == True:
                datasetname = 'LLI_mirror_short_time'
            else:
                datasetname = 'LLI_no_mirror_short_time'
        else:
            if self.parameters.Parity_LLI.mirror_state == True:
                datasetname = 'LLI_mirror_long_time'
            else:
                datasetname = 'LLI_no_mirror_long_time'
        dataset_in_folder = self.dv.dir(context= self.save_data)[1]
        names = sorted([name for name in dataset_in_folder if datasetname in name])
        if names:
            #dataset with that name exist
            self.dv.open_appendable(names[0],context=self.save_data)
        else:
            #dataset doesn't already exist
            self.dv.new(datasetname,[('Time', 'Sec')],[('Parity','Parity_phase','Probability'),
                                                       ('Parity','Parity_phase_plus_pi','Probability'),
                                                       ('Parity','Parity_error_signal','Probability'),
                                                       ('Parity','Phase','Degrees'),
                                                       ('Excitation','Single_ion','Probability'),
                                                       ],context=self.save_data)
            window_name = [datasetname]
            self.dv.add_parameter('Window', window_name,context=self.save_data)
            self.dv.add_parameter('plotLive', True,context=self.save_data) 
            time_string = str(datetime.datetime.now())
            self.dv.add_parameter('Start_time', time_string,context=self.save_data)
        
    def run(self, cxn, context):
        #print 'Running Phase Tracker with Mirroring:',self.parameters.Parity_LLI.mirror_state
        self.setup_data_vault()
        #run with phase without adding pi
        #run with crystallization
        excitation_phase, readouts_phase = self.get_excitation_crystallizing(False, cxn, context)    
        #computer parity
        if self.parameters.StateReadout.use_camera_for_readout:
            position1 = int(self.parameters.Parity_transitions.left_ion_number)
            position2 = int(self.parameters.Parity_transitions.right_ion_number)
            parity_phase = self.compute_parity(readouts_phase,position1,position2)
        else:
            threshold_low = self.parameters.StateReadout.parity_threshold_low
            threshold_high = self.parameters.StateReadout.parity_threshold_high
            parity_phase = self.compute_parity_pmt(readouts_phase,threshold_low,threshold_high)
        
        #run with phase plus pi
        #run with crystallization
        excitation_phase_plus_pi, readouts_phase_plus_pi = self.get_excitation_crystallizing(True, cxn, context)    
        #computer parity
        if self.parameters.StateReadout.use_camera_for_readout:
            position1 = int(self.parameters.Parity_transitions.left_ion_number)
            position2 = int(self.parameters.Parity_transitions.right_ion_number)
            parity_phase_plus_pi = self.compute_parity(readouts_phase_plus_pi,position1,position2)
        else:
            threshold_low = self.parameters.StateReadout.parity_threshold_low
            threshold_high = self.parameters.StateReadout.parity_threshold_high
            parity_phase_plus_pi = self.compute_parity_pmt(readouts_phase_plus_pi,threshold_low,threshold_high)

        
        ## get starting phase ##
        if self.parameters.Parity_LLI.use_short_ramsey_time:
            if self.parameters.Parity_LLI.mirror_state:
                starting_phase = self.parameters.Parity_LLI.phase_mirror_state_short_time
            else:
                starting_phase = self.parameters.Parity_LLI.phase_no_mirror_state_short_time
        else:
            if self.parameters.Parity_LLI.mirror_state:
                starting_phase = self.parameters.Parity_LLI.phase_mirror_state
            else:
                starting_phase = self.parameters.Parity_LLI.phase_no_mirror_state
        
        parity_error_signal = (parity_phase-parity_phase_plus_pi)/2.0
        total_excitation = (excitation_phase[0]-excitation_phase_plus_pi[0])/2.0
        phase_offset = starting_phase + self.compute_phase_correction(parity_error_signal)
        
        #submit data for single ion excitation
        ##compute time now##
        data_time = datetime.datetime.now().hour*3600+datetime.datetime.now().minute*60+datetime.datetime.now().second
        
        submission = [data_time,
                      parity_phase,
                      parity_phase_plus_pi,
                      parity_error_signal,
                      phase_offset['deg'],
                      total_excitation]
        self.dv.add(submission,context=self.save_data)
        ### phase feedback update to PV###
        if self.parameters.Parity_LLI.phase_feedback:
            if self.parameters.Parity_LLI.use_short_ramsey_time:
                if self.parameters.Parity_LLI.mirror_state:
                    self.pv.set_parameter('Parity_LLI','phase_mirror_state_short_time',phase_offset)
                else:
                    self.pv.set_parameter('Parity_LLI','phase_no_mirror_state_short_time',phase_offset)
            else:
                if self.parameters.Parity_LLI.mirror_state:
                    self.pv.set_parameter('Parity_LLI','phase_mirror_state',phase_offset)
                else:
                    self.pv.set_parameter('Parity_LLI','phase_no_mirror_state',phase_offset)
        #self.update_progress(i)
        
        return phase_offset
    
    def get_excitation_crystallizing(self, phase_plus_pi, cxn, context):
        self.setup_sequence_parameters(phase_plus_pi)
        self.excite.set_parameters(self.parameters)
        self.update_mirror_state(phase_plus_pi)
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
    
    def compute_phase_correction(self, parity_signal):
        '''
        computes the correction of the phase 
        '''
        contrast = self.parameters.Parity_LLI.contrast
        if np.abs(parity_signal) > contrast:
            error_signal = -1*np.sign(parity_signal)*90.0
        else:
            error_signal = np.arccos(parity_signal/contrast)*180/np.pi-90.0
        return WithUnit(error_signal, 'deg')
    
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
        #self.save_parameters(self.dv, cxn, self.cxnlab, self.save_phase)
        #self.save_parameters(self.dv, cxn, self.cxnlab, self.save_parity)
        #self.save_parameters(self.dv, cxn, self.cxnlab, self.save_single_ion_signal)
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
    exprt = Parity_LLI_phase_tracker(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)