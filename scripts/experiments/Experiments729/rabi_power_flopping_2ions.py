from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_rabi_2ions
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import numpy as np
import time
import labrad
from labrad.units import WithUnit
#from numpy import linspace

class Rabi_power_flopping_2ions(experiment):
    
    name = 'Rabi_power_flopping_2ions'
    trap_frequencies = [
                        ('TrapFrequencies','axial_frequency'),
                        ('TrapFrequencies','radial_frequency_1'),
                        ('TrapFrequencies','radial_frequency_2'),
                        ('TrapFrequencies','rf_drive_frequency'),                       
                        ]
    rabi_required_parameters = [
                           ('RabiPowerFlopping_2ions','ion1_manual_frequency_729'),
                           ('RabiPowerFlopping_2ions','ion1_line_selection'),
                           ('RabiPowerFlopping_2ions','ion1_frequency_selection'),
                           ('RabiPowerFlopping_2ions','ion1_sideband_selection'),
                           ('RabiPowerFlopping_2ions','ion1_excitation_duration'),
                           
                           ('RabiPowerFlopping_2ions','block_ion1_729'),
                           
                           ('RabiPowerFlopping_2ions','block_ion2_729'),
                           
                           ('RabiPowerFlopping_2ions','auto_fit'),

                           ('RabiPowerFlopping_2ions','ion2_manual_frequency_729'),
                           ('RabiPowerFlopping_2ions','ion2_line_selection'),
                           ('RabiPowerFlopping_2ions','ion2_frequency_selection'),
                           ('RabiPowerFlopping_2ions','ion2_sideband_selection'),
                           ('RabiPowerFlopping_2ions','ion2_excitation_duration'),
                           
                           ('RabiPowerFlopping_2ions','manual_power_scan'),
                           ('RabiPowerFlopping_2ions','log_scale_scan'),
                           
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
        parameters = set(cls.rabi_required_parameters)
        parameters = parameters.union(set(cls.trap_frequencies))
        parameters = parameters.union(set(excitation_rabi_2ions.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Rabi_excitation_729_2ions','ion1_excitation_frequency'))
        parameters.remove(('Rabi_excitation_729_2ions','ion1_excitation_amplitude'))
        parameters.remove(('Rabi_excitation_729_2ions','ion1_excitation_duration'))
        parameters.remove(('Rabi_excitation_729_2ions','ion2_excitation_frequency'))
        parameters.remove(('Rabi_excitation_729_2ions','ion2_excitation_amplitude'))
        parameters.remove(('Rabi_excitation_729_2ions','ion2_excitation_duration'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation_rabi_2ions)
        self.excite.initialize(cxn, context, ident)
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.auto_fit = self.parameters.RabiPowerFlopping_2ions.auto_fit
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.rabi_flop_save_context = cxn.context()
    
    def setup_sequence_parameters(self):
        self.load_frequency()
        flop = self.parameters.RabiPowerFlopping_2ions
        self.parameters['Rabi_excitation_729_2ions.ion1_excitation_duration'] = flop.ion1_excitation_duration
        self.parameters['Rabi_excitation_729_2ions.ion2_excitation_duration'] = flop.ion2_excitation_duration
        minim,maxim,steps = flop.manual_power_scan
        minim = minim['dBm']; maxim = maxim['dBm']
        if flop.log_scale_scan:
            #print "log scale"
            self.scan = np.linspace(10**(minim/10),10**(maxim/10),num=steps)
            self.scan = 10*np.log10(self.scan)
            self.scan = [WithUnit(pt, 'dBm') for pt in self.scan]
        else:
            #print "linear scale"
            self.scan = np.linspace(minim,maxim, steps)
            self.scan = [WithUnit(pt, 'dBm') for pt in self.scan]
        
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        self.directory_for_fitter = directory
        self.dv.cd(directory ,True, context = self.rabi_flop_save_context)
        output_size = self.excite.output_size
        dependants = [('Excitation','Ion {}'.format(ion),'Probability') for ion in range(output_size)]
        self.dv.new('Rabi Power Flopping {}'.format(datasetNameAppend),[('Excitation', 'dBm')], dependants , context = self.rabi_flop_save_context)
        self.dv.add_parameter('Window', ['Rabi Power Flopping'], context = self.rabi_flop_save_context)
        self.dv.add_parameter('plotLive', True, context = self.rabi_flop_save_context)
    
    def load_frequency(self):
        #reloads trap frequencyies and gets the latest information from the drift tracker
        self.reload_some_parameters(self.trap_frequencies) 
        flop = self.parameters.RabiPowerFlopping_2ions
        frequency1 = cm.frequency_from_line_selection(flop.ion1_frequency_selection, flop.ion1_manual_frequency_729, flop.ion1_line_selection, self.drift_tracker)
        frequency2 = cm.frequency_from_line_selection(flop.ion2_frequency_selection, flop.ion2_manual_frequency_729, flop.ion2_line_selection, self.drift_tracker)
        trap = self.parameters.TrapFrequencies
        if flop.ion1_frequency_selection == 'auto':
            frequency1 = cm.add_sidebands(frequency1, flop.ion1_sideband_selection, trap)
        if flop.ion2_frequency_selection == 'auto':
            frequency2 = cm.add_sidebands(frequency2, flop.ion2_sideband_selection, trap)
        self.parameters['Rabi_excitation_729_2ions.ion1_excitation_frequency'] = frequency1
        self.parameters['Rabi_excitation_729_2ions.ion2_excitation_frequency'] = frequency2
        
    def run(self, cxn, context):
        self.setup_data_vault()
        self.setup_sequence_parameters()
        for i,power in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            excitation = self.get_excitation_crystallizing(cxn, context, power)
            if excitation is None: break 
            submission = [power['dBm']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.rabi_flop_save_context)
            self.update_progress(i)
        if not should_stop:
            result_power, accepted = self.get_target_power(cxn, context)
        else:
            result_power = WithUnit(-63.0,'dBm')
            accepted = False
        return result_power, accepted
            
    def get_target_power(self, cxn, context):
        self.fitter = cxn.fitter
        directory = (self.directory_for_fitter,1)
        self.fitter.load_data(directory)
        print self.auto_fit
        self.fitter.fit('Rabi_power_flop', self.auto_fit)
        accepted = self.fitter.wait_for_acceptance()
        if accepted:
            target_power = WithUnit(self.fitter.get_parameter('target_power'),'dBm')
        else:
            target_power = WithUnit(-63.0,'dBm')
        return target_power, accepted
        
    
    def get_excitation_crystallizing(self, cxn, context, power):
        excitation = self.do_get_excitation(cxn, context, power)
        if self.parameters.Crystallization.auto_crystallization:
            initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
            #if initially melted, redo the point
            while initally_melted:
                if not got_crystallized:
                    #if crystallizer wasn't able to crystallize, then pause and wait for user interaction
                    self.cxn.scriptscanner.pause_script(self.ident, True)
                    should_stop = self.pause_or_stop()
                    if should_stop: return None
                excitation = self.do_get_excitation(cxn, context, power)
                initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
        return excitation
    
    def do_get_excitation(self, cxn, context, power):
        self.load_frequency()
        power_off = WithUnit(-63.0,'dBm')
        if self.parameters.RabiPowerFlopping_2ions.block_ion1_729:
            self.parameters['Rabi_excitation_729_2ions.ion1_excitation_amplitude'] = power_off
        else:
            self.parameters['Rabi_excitation_729_2ions.ion1_excitation_amplitude'] = power
        if self.parameters.RabiPowerFlopping_2ions.block_ion2_729:
            self.parameters['Rabi_excitation_729_2ions.ion2_excitation_amplitude'] = power_off
        else:
            self.parameters['Rabi_excitation_729_2ions.ion2_excitation_amplitude'] = power
        self.excite.set_parameters(self.parameters)
        self.excite.setup_sequence_parameters()
        excitation, readouts = self.excite.run(cxn, context)
        return excitation
     
    def finalize(self, cxn, context):
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
    exprt = Rabi_power_flopping_2ions(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)