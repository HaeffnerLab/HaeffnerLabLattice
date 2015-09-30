from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_ramsey_with_heating
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace
#The following command brinfgs the sequence plotter.
#from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter

class ramsey_with_heating_and_cryst(experiment):
    
    name = 'Ramsey_with_Heating_Pulse_and_Cryst'
    ramsey_with_heating_required_parameters = [
                           ('Dephasing_Pulses', 'preparation_line_selection'),
                           ('Dephasing_Pulses', 'evolution_line_selection'),
                           ('Dephasing_Pulses', 'preparation_sideband_selection'),
                           ('Dephasing_Pulses', 'evolution_sideband_selection'),
                           ('Dephasing_Pulses', 'scan_interaction_duration'),
                           ('Dephasing_Pulses', 'scan_phase'), #Ahmed
                           ('Dephasing_Pulses', 'analysis_ion_number'), # Dylan -- ion number we want to read out
                           ('Dephasing_Pulses', 'mode_offset'), #Ahmed
                           
                           ('Crystallization', 'auto_crystallization'),
                           ('Crystallization', 'camera_record_exposure'),
                           ('Crystallization', 'camera_threshold'),
                           ('Crystallization', 'max_attempts'),
                           ('Crystallization', 'max_duration'),
                           ('Crystallization', 'min_duration'),
                           ('Crystallization', 'pmt_record_duration'),
                           ('Crystallization', 'pmt_threshold'),
                           ('Crystallization', 'use_camera'),

                           ('TrapFrequencies','axial_frequency'),
                           ('TrapFrequencies','radial_frequency_1'),
                           ('TrapFrequencies','radial_frequency_2'),
                           ('TrapFrequencies','rf_drive_frequency'),
                           ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.ramsey_with_heating_required_parameters)
        parameters = parameters.union(set(excitation_ramsey_with_heating.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Dephasing_Pulses','evolution_ramsey_time'))
        parameters.remove(('Dephasing_Pulses','evolution_pulses_frequency'))
        parameters.remove(('Dephasing_Pulses','preparation_pulse_frequency'))
        parameters.remove(('Dephasing_Pulses','evolution_pulses_phase'))  #Ahmed
        parameters.remove(('Dephasing_Pulses','mode_offset')) #Ahmed
        return parameters
        
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation_ramsey_with_heating)
        self.excite.initialize(cxn, context, ident)

        # adding crystallization process
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
 
        self.scan = []
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        #self.cxnlab = labrad.connect('localhost') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.data_save_context = cxn.context()
        self.contrast_save_context = cxn.context() # for saving the contrast 
        
        minim_t,maxim_t,t_steps = self.parameters.Dephasing_Pulses.scan_interaction_duration #Ahmed
        minim_phi,maxim_phi,phi_steps = self.parameters.Dephasing_Pulses.scan_phase #Ahmed
        minim_t = minim_t['us']; maxim_t = maxim_t['us']  #Ahmed
        minim_phi = minim_phi['deg']; maxim_phi = maxim_phi['deg']  #Ahmed

        self.scan_t = linspace(minim_t,maxim_t, t_steps)  #Ahmed
        self.scan_t = [WithUnit(pt_t, 'us') for pt_t in self.scan_t]  #Ahmed

        self.scan_phi = linspace(minim_phi,maxim_phi, phi_steps)  #Ahmed
        self.scan_phi = [WithUnit(pt_phi, 'deg') for pt_phi in self.scan_phi]  #Ahmed
       
        self.radial_freq_offset = self.parameters.Dephasing_Pulses.mode_offset #Ahmed               

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
            frequency_evolution = frequency_evolution + radial_freq_offset #Ahmed
            print 'Displaced Sideband:', frequency_evolution #Ahmed
        self.parameters['Dephasing_Pulses.preparation_pulse_frequency'] = frequency_preparation
        self.parameters['Dephasing_Pulses.evolution_pulses_frequency'] = frequency_evolution
        self.max_second_pulse = p.evolution_pulses_duration

        
    def setup_data_vault(self):
        localtime = time.localtime()
        dirappend = [time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.dv.cd(directory, True,context = self.data_save_context)
        self.dv.cd(directory, True,context = self.contrast_save_context)
        
    def data_vault_new_trace(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        contrastDatasetNameAppend = datasetNameAppend + '_contrast'
        #output_size = self.excite.output_size
        #output_size = 4
        #dependants = [('Excitation','Ion {}'.format(ion),'Probability') for ion in range(output_size)]
        
        #dependants = [('Excitation','Phase {}'.format(phase),'Probability') for phase in self.scan_phi]
        
        dependants = [('Excitation','Phase {0}'.format(phase),'Probability') for phase in self.scan_phi]

        self.dv.new('{0} {1}'.format(self.name, datasetNameAppend),[('Excitation', 'us')], dependants , context = self.data_save_context)
        window_name = ['Ramsey with Heating - Scan Ramsey Gap + Phase']
        self.dv.add_parameter('Window', window_name, context = self.data_save_context)
        self.dv.add_parameter('plotLive', True, context = self.data_save_context)
        
        # context for saving the contrast of the phis
        dependants = [('Contrast','Contrast','Arb')]
        self.dv.new('{0} {1}'.format(self.name, contrastDatasetNameAppend),[('Excitation', 'us')], dependants , context = self.contrast_save_context)
        window_name = ['Dephasing, Contrast - Scan Ramsey Gap + Phase']
        self.dv.add_parameter('Window', window_name, context = self.contrast_save_context)
        self.dv.add_parameter('plotLive', True, context = self.contrast_save_context)
               
        
    def run(self, cxn, context):
        
        p = self.parameters.Dephasing_Pulses

        self.data_vault_new_trace()
        self.setup_sequence_parameters()
        for i,interaction_duration in enumerate(self.scan_t):
            
            #second_pulse_dur = min(self.max_second_pulse, interaction_duration)
            #ramsey_time = max(WithUnit(0,'us'), interaction_duration - self.max_second_pulse)            
            #p.evolution_ramsey_time = ramsey_time
            #p.evolution_pulses_duration = second_pulse_dur
            
            p.evolution_ramsey_time = interaction_duration
            ramsey_time = p.evolution_ramsey_time
            
            N = int(p.analysis_ion_number) # index from 0
            #print N
            #-------------------- Phase loop
            submission = [interaction_duration['us']] #This is the time
            phase_list = []
            for j,interaction_phase in enumerate(self.scan_phi):                
                p.evolution_pulses_phase = interaction_phase #added for the phase steps

                should_stop = self.pause_or_stop()
                if should_stop:
                    return False
                
                
                if self.parameters.Heating.enable_heating_pulse:
                    frequency_advance_duration = WithUnit(6, 'us')
                    total_heating_time = frequency_advance_duration + self.parameters.Heating.blue_heating_duration + self.parameters.Heating.blue_heating_repump_additional                
                    # the ramsey pulse has to start after the blue_delay_before and the total_heating_duration
                    # ramsey_time is the REAL time between the two pi/2 pulses
                    min_ramsey_time = ramsey_time - total_heating_time - self.parameters.Heating.blue_heating_delay_before
                    
                    # setting the time after to zero, since this will be calculated with the gap time
                    self.parameters.Heating.blue_heating.delay_after = WithUnit(0.0, 'us')                
                    
                    if min_ramsey_time.value < 0:
                        print "Sequence not possible, ramsey pulse overlaps with heating pulse"
                        print "Min scan_duration you need is ", total_heating_time + self.parameters.Heating.blue_heating_delay_before
                        print "Ramsey pulse length", ramsey_time
                        print "Ramsey pulse start", self.max_second_pulse                    
                        print "total_heating_time", total_heating_time
                        print "start of blue pulse", self.parameters.Heating.blue_heating_delay_before                    
                        return False                

                # run the experiment with the crystallization
                excitation = self.get_excitation_crystallizing(cxn, context)
                if excitation is None: break

                # excitation looks like [ion1 excit, ion2 ex, ... ]
                # pull out just the ion readout we care about with excitation[N]
                phase_list.append(excitation[N]) # only look at the excitation for the ion we readout

            submission.extend(phase_list) # The excitation is attached to the time now in a second column (?)
            self.dv.add(submission, context = self.data_save_context) #Saving to data file where submission now includes the time and excitation
            
            # now have submitted raw data, save contrast for online analysis
            try:
                contrast = (max(phase_list) - min(phase_list))/(max(phase_list) + min(phase_list)) # will fail with 0 excitation
            except:
                contrast = 0 # in case there's no excitation
            contrast_submission = [interaction_duration['us'], contrast]
            self.dv.add(contrast_submission, context = self.contrast_save_context)

            self.update_progress(i)
        self.save_parameters(self.dv, cxn, self.cxnlab, self.data_save_context)
        ####### PULSE SEQUENCE PLOTTING #########
        #ttl = self.cxn.pulser.human_readable_ttl()
        #dds = self.cxn.pulser.human_readable_dds()
        #channels = self.cxn.pulser.get_channels().asarray
        #sp = SequencePlotter(ttl.asarray, dds.aslist, channels)
        #sp.makePlot()
        ############################################
        return True

    def get_excitation_crystallizing(self, cxn, context):
        excitation = self.do_get_excitation(cxn, context)
        if self.parameters.Crystallization.auto_crystallization:
            initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
            #if initially melted, redo the point
            while initally_melted:
                if not got_crystallized:
                    #if crystallizer wasn't able to crystallize, then pause and wait for user interaction
                    self.cxn.scriptscanner.pause_script(self.ident, True)
                    should_stop = self.pause_or_stop()
                    if should_stop: return None
                excitation = self.do_get_excitation(cxn, context)
                initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
        return excitation
    
    def do_get_excitation(self, cxn, context):
        self.excite.set_parameters(self.parameters)
        excitation, readouts = self.excite.run(cxn, context)
        return excitation

    def finalize(self, cxn, context):
        pass

    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan_t)
        self.sc.script_set_progress(self.ident,  progress)

    def save_parameters(self, dv, cxn, cxnlab, context):
        measuredDict = dvParameters.measureParameters(cxn, cxnlab)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ramsey_with_heating_and_cryst(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
