from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_ramsey_2ions
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
#from numpy import linspace
import numpy as np

class Parity_LLI_phase_tracker(experiment):
    
    name = 'Parity_LLI_phase_tracker'
    Parity_LLI_required_parameters = [
                           ('Parity_LLI', 'mirror_state'),
                           ('Parity_LLI', 'ramsey_time'),
                           ('Parity_LLI', 'phase_feedback'),
                           ('Parity_LLI', 'phase_mirror_state'),
                           ('Parity_LLI', 'phase_no_mirror_state'),
        
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
        self.save_phase = cxn.context()
        self.save_parity = cxn.context()
        self.save_single_ion_signal = cxn.context()
        self.excite = self.make_experiment(excitation_ramsey_2ions)
        self.excite.initialize(cxn, context, ident)
        
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
            self.parameters['Ramsey_2ions.ion2_excitation_phase1'] = self.parameters['Parity_LLI.phase_no_mirror_state']     
        self.parameters['Ramsey_2ions.ramsey_time'] = self.parameters['Parity_LLI.ramsey_time']
        
    def setup_data_vault(self):
        localtime = time.localtime()
        ### save result fot long term tracking ###
        directory_LLI = ['','Drift_Tracking','LLI_tracking']
        directory_LLI.append(time.strftime("%Y%b%d",localtime))
        ### save parity###
        self.dv.cd(directory_LLI ,True, context = self.save_parity)
        if self.parameters.Parity_LLI.mirror_state == True:
            datasetname_parity = 'LLI_parity_mirror'
        else:
            datasetname_parity = 'LLI_parity_no_mirror'
        dataset_parity_in_folder = self.dv.dir(context= self.save_parity)[1]
        names = sorted([name for name in dataset_parity_in_folder if datasetname_parity in name])
        if names:
            #dataset with that name exist
            self.dv.open_appendable(names[0],context=self.save_parity)
        else:
            #dataset doesn't already exist
            self.dv.new(datasetname_parity,[('Time', 'Sec')],[('Parity','Parity','Probability')],context=self.save_parity)
            window_name = [datasetname_parity]
            self.dv.add_parameter('Window', window_name,context=self.save_parity)
            self.dv.add_parameter('plotLive', True,context=self.save_parity)    
        ### save individual ion ###
        output_size = self.excite.output_size
        dependants = [('Excitation','Ion {}'.format(ion),'Probability') for ion in range(output_size)]
        self.dv.cd(directory_LLI ,True, context = self.save_single_ion_signal)
        if self.parameters.Parity_LLI.mirror_state == True:
            datasetname_single_ion = 'LLI_single_ion_mirror'
        else:
            datasetname_single_ion = 'LLI_single_ion_no_mirror'
        dataset_single_ion_in_folder = self.dv.dir(context= self.save_single_ion_signal)[1]
        names = sorted([name for name in dataset_single_ion_in_folder if datasetname_single_ion in name])
        if names:
            #dataset with that name exist
            self.dv.open_appendable(names[0],context=self.save_single_ion_signal)
        else:
            #dataset doesn't already exist
            self.dv.new(datasetname_single_ion,[('Time', 'Sec')],dependants,context=self.save_single_ion_signal)
            window_name = [datasetname_single_ion]
            self.dv.add_parameter('Window', window_name,context=self.save_single_ion_signal)
            self.dv.add_parameter('plotLive', True,context=self.save_single_ion_signal)
        ### save phase ###
        self.dv.cd(directory_LLI ,True, context = self.save_phase)
        if self.parameters.Parity_LLI.mirror_state == True:
            datasetnamephase = 'LLI_phase_mirror'
        else:
            datasetnamephase = 'LLI_phase_no_mirror'
        datasetphase_in_folder = self.dv.dir(context=self.save_phase)[1]
        names = sorted([name for name in datasetphase_in_folder if datasetnamephase in name])
        if names:
            #dataset with that name exist
            self.dv.open_appendable(names[0],context=self.save_phase)
        else:
            #dataset doesn't already exist
            self.dv.new(datasetnamephase,[('Time', 'Sec')],[('Phase','deg','Phase')],context=self.save_phase)
            window_name = [datasetnamephase]
            self.dv.add_parameter('Window', window_name,context=self.save_phase)
            self.dv.add_parameter('plotLive', True,context=self.save_phase)
        
    def run(self, cxn, context):
        print 'Running Phase Tracker with Mirroring:',self.parameters.Parity_LLI.mirror_state
        self.setup_data_vault()
        self.setup_sequence_parameters()
        self.excite.set_parameters(self.parameters)
        if self.parameters.Parity_LLI.mirror_state:
            starting_phase = self.parameters.Parity_LLI.phase_mirror_state
        else:
            starting_phase = self.parameters.Parity_LLI.phase_no_mirror_state
        excitation,readouts = self.excite.run(cxn, context)
        position1 = int(self.parameters.Parity_transitions.left_ion_number)
        position2 = int(self.parameters.Parity_transitions.right_ion_number)
        parity = self.compute_parity(readouts,position1,position2)
        ## calculate phase_offset ##
        phase_offset = starting_phase + self.compute_phase_correction(parity)
        #print phase_offset, starting_phase, self.compute_phase_correction(parity)
        submission_single_ion = [time.time()]
        submission_single_ion.extend(excitation)
        self.dv.add([time.time(), parity],context=self.save_parity)
        self.dv.add(submission_single_ion,context=self.save_single_ion_signal)
        self.dv.add([time.time(), phase_offset['deg']],context=self.save_phase)
        ### phase feedback ###
        #phase_offset_modulo = WithUnit(np.mod(phase_offset,360),'deg')
        if self.parameters.Parity_LLI.phase_feedback:
            if self.parameters.Parity_LLI.mirror_state:
                self.pv.set_parameter('Parity_LLI','phase_mirror_state',phase_offset)
            else:
                self.pv.set_parameter('Parity_LLI','phase_no_mirror_state',phase_offset)
        #self.update_progress(i)
        return phase_offset
    
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
        contrast = 0.5
        #error_signal = WithUnit(parity_signal*180.0/(contrast*2.0*np.pi),'deg')
        if np.abs(parity_signal) > contrast:
            error_signal = -1*np.sign(parity_signal)*90.0
        else:
            error_signal = np.arccos(parity_signal/contrast)*180/np.pi-90.0
        return WithUnit(error_signal, 'deg')
     
    def finalize(self, cxn, context):
        #self.save_parameters(self.dv, cxn, self.cxnlab, self.save_parity)
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