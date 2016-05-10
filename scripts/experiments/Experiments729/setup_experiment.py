from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_729

from take_spectrum_to_fit import take_spectrum_to_fit

from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
import numpy as np

from treedict import TreeDict


class setup_experiment(experiment):
    
    name = 'Setup_Experiment'
    setup_experiment_required_parameters = [
                           ('Spectrum','custom'),
                           ('Spectrum','normal'),
                           ('Spectrum','fine'),
                           ('Spectrum','ultimate'),
                           
                           ('Spectrum','line_selection'),
                           ('Spectrum','manual_amplitude_729'),
                           ('Spectrum','manual_excitation_time'),
                           ('Spectrum','manual_scan'),
                           ('Spectrum','scan_selection'),
                           ('Spectrum','sensitivity_selection'),
                           ('Spectrum','sideband_selection'),

                           ('TrapFrequencies','axial_frequency'),
                           ('TrapFrequencies','radial_frequency_1'),
                           ('TrapFrequencies','radial_frequency_2'),
                           ('TrapFrequencies','rf_drive_frequency'),
                           
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
    
    spectrum_optional_parmeters = [
                          ('Spectrum', 'window_name')
                          ]
    
    remove_parameters = [
        ('Display', 'relative_frequencies'),

        ('StateReadout', 'repeat_each_measurement'),
        ('StateReadout', 'use_camera_for_readout'),
        
        ('StatePreparation', 'sideband_cooling_enable'),
        ('StatePreparation', 'optical_pumping_enable'),
        ('Excitation_729', 'bichro'),
        ('Excitation_729', 'channel_729')]
      
                                       
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.setup_experiment_required_parameters)
        parameters = parameters.union(set(take_spectrum_to_fit.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        
        for p in cls.remove_parameters:            
            parameters.remove(p)
        #parameters.remove(('Excitation_729','rabi_excitation_amplitude'))
        #parameters.remove(('Excitation_729','rabi_excitation_duration'))
        #parameters.remove(('Excitation_729','rabi_excitation_frequency'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        
        self.excite = self.make_experiment(take_spectrum_to_fit)
        self.excite.initialize(cxn, context, ident)
        
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
        
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.pv = cxn.parametervault
        try:
            self.grapher = cxn.grapher
        except: self.grapher = None
        self.spectrum_save_context = cxn.context()    
        
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        
        #self.directory_for_fitter = directory
        
        self.dv.cd(directory ,True, context = self.spectrum_save_context)
                
        output_size = 1 # just a single ion for the time being
        dependants = [('Excitation','Ion {}'.format(ion),'Probability') for ion in range(output_size)]
         
        #self.dv.new('Spectrum {}'.format(datasetNameAppend),[('Excitation', 'us')], dependants , context = self.spectrum_save_context)
         
        #if self.grapher is not None:
        #    self.grapher.plot_with_axis(ds, window_name, sc, False)
 
        #window_name = ['Automation test']
         
        #self.dv.add_parameter('Window', window_name, context = self.spectrum_save_context)
        #self.dv.add_parameter('plotLive', True, context = self.spectrum_save_context)
        
        
    def run(self, cxn, context):
        #self.setup_data_vault()            

	    # initial rough scan 
        # Spectrum parameters
        s12d12 = -14.61
        delta_s12d12 = 0.4/2
        no_of_steps = 30
        
        excitation_time_1212 = 50.0
        
        amplitude = -18.0
       
        
        replace_1 = TreeDict.fromdict({
                                       'Spectrum.manual_scan':(WithUnit(s12d12 - delta_s12d12, 'MHz'), WithUnit(s12d12 + delta_s12d12, 'MHz'), no_of_steps),
                                       'Spectrum.manual_amplitude_729':WithUnit(amplitude, 'dBm'),
                                       'Spectrum.manual_excitation_time':WithUnit(excitation_time_1212, 'us'),
                                       'Spectrum.scan_selection':'manual',
                                       'StatePreparation.sideband_cooling_enable':False,
                                       'StatePreparation.optical_pumping_enable':True,
                                       'Display.relative_frequencies':False,
                                       'StateReadout.repeat_each_measurement':100,
                                       'StateReadout.use_camera_for_readout':False,
                                       'Excitation_729.bichro':False,
                                       'Excitation_729.channel_729':'729local',
                                       'Spectrum.window_name':['car1']                                      
                                       })
        
        
        drift_line1 = TreeDict.fromdict({
                                       'DriftTrackerRamsey.line_selection':'S-1/2D-1/2',                                       
                                       'DriftTrackerRamsey.detuning':WithUnit(0,'Hz')                                       
                                       })
        

        self.excite.set_parameters(replace_1)
        fitted_freq1 = self.excite.run(cxn, context)



	    # fine scan
    	no_of_steps = 40
    	amplitude = -25.0

        s12d12 = fitted_freq1
        delta_s12d12 = 0.04/2
        excitation_time_1212 = 400.0

        replace_1 = TreeDict.fromdict({
                                       'Spectrum.manual_scan':(WithUnit(s12d12 - delta_s12d12, 'MHz'), WithUnit(s12d12 + delta_s12d12, 'MHz'), no_of_steps),
                                       'Spectrum.manual_amplitude_729':WithUnit(amplitude, 'dBm'),
                                       'Spectrum.manual_excitation_time':WithUnit(excitation_time_1212, 'us'),
                                       'Spectrum.scan_selection':'manual',
                                       'Display.relative_frequencies':False,
                                       'StateReadout.repeat_each_measurement':100,
                                       'StateReadout.use_camera_for_readout':False,
                                       'Excitation_729.bichro':False,
                                       'Excitation_729.channel_729':'729local',
                                       'Spectrum.window_name':['car1']
                                       })
 
  
        drift_line1 = TreeDict.fromdict({
                                       'DriftTrackerRamsey.line_selection':'S-1/2D-1/2',                                       
                                       'DriftTrackerRamsey.detuning':WithUnit(0,'Hz')                                       
                                       })

 
        self.excite.set_parameters(replace_1)
        fitted_freq1 = self.excite.run(cxn, context)


	#### D5/2 

        s12d52 = -25.70
        delta_s12d52 = 0.4/2
    	excitation_time_1252 = 50.0
    	amplitude = -18.0
        no_of_steps = 30

       

        replace_2 = TreeDict.fromdict({
                                       'Spectrum.manual_scan':(WithUnit(s12d52 - delta_s12d52, 'MHz'), WithUnit(s12d52 + delta_s12d52, 'MHz'), no_of_steps),
                                       'Spectrum.manual_amplitude_729':WithUnit(amplitude, 'dBm'),
                                       'Spectrum.manual_excitation_time':WithUnit(excitation_time_1252, 'us'),
                                       'Spectrum.scan_selection':'manual',
                                       'Display.relative_frequencies':False,
                                       'StateReadout.repeat_each_measurement':100,
                                       'StateReadout.use_camera_for_readout':False,
                                       'Excitation_729.bichro':False,
                                       'Excitation_729.channel_729':'729local',
                                       'Spectrum.window_name':['car2']
                                       })

        drift_line2 = TreeDict.fromdict({
                                       'DriftTrackerRamsey.line_selection':'S-1/2D-5/2',                                       
                                       'DriftTrackerRamsey.detuning':WithUnit(0,'Hz')                                       
                                       })
        
               
        self.excite.set_parameters(replace_2)
        fitted_freq2 = self.excite.run(cxn, context)
 

        # fine scan
        s12d52 = fitted_freq2
        amplitude = -25.0
        no_of_steps = 40

        delta_s12d52 = 0.04/2
        
        excitation_time_1252 = 400.0

       
        replace_2 = TreeDict.fromdict({
                                       'Spectrum.manual_scan':(WithUnit(s12d52 - delta_s12d52, 'MHz'), WithUnit(s12d52 + delta_s12d52, 'MHz'), no_of_steps),
                                       'Spectrum.manual_amplitude_729':WithUnit(amplitude, 'dBm'),
                                       'Spectrum.manual_excitation_time':WithUnit(excitation_time_1252, 'us'),
                                       'Spectrum.scan_selection':'manual',
                                       'Display.relative_frequencies':False,
                                       'StateReadout.repeat_each_measurement':100,
                                       'StateReadout.use_camera_for_readout':False,
                                       'Excitation_729.bichro':False,
                                       'Excitation_729.channel_729':'729local',
                                       'Spectrum.window_name':['car2']
                                       })
              
        drift_line2 = TreeDict.fromdict({
                                       'DriftTrackerRamsey.line_selection':'S-1/2D-5/2',                                       
                                       'DriftTrackerRamsey.detuning':WithUnit(0,'Hz')                                       
                                       })
        
               
        self.excite.set_parameters(replace_2)
        fitted_freq2 = self.excite.run(cxn, context)
       


 
        # taking scan over the -1/2 -1/2 line
        #self.excite.set_progress_limits(0, 50.0)
        
        #self.excite.set_progress_limits(50.0, 100.0)
        
        submission = [fitted_freq1]
        submission.extend([fitted_freq1])
        self.dv.add(submission, context = self.spectrum_save_context)

        print "in main exp " + str(fitted_freq1)
        print "in main exp " + str(fitted_freq2)
        
        if (fitted_freq1 != 0.0) and (fitted_freq2 != 0.0):
            self.submit_centers(drift_line1, WithUnit(fitted_freq1, 'MHz'), drift_line2, WithUnit(fitted_freq2, 'MHz'))
  
            # setting some parameters for the drift tracker
            #self.pv.set_parameter('DriftTrackerRamsey', 'line_1_pi_time', WithUnit(5.0, 'us'))
            #self.pv.set_parameter('DriftTrackerRamsey', 'line_2_pi_time', WithUnit(5.0, 'us'))
  
        # fit the result
        # make two new sequences that fit a line and give the result and one that fits a rabi and gives the result
        #self.fit_center_freq(cxn, context)
                

    def submit_centers(self, replace_1, center1, replace_2, center2):     
        if center1 is not None and center2 is not None:
            submission = [                          
                          (replace_1.DriftTrackerRamsey.line_selection, center1),
                          (replace_2.DriftTrackerRamsey.line_selection, center2),
                          ]
            self.drift_tracker.set_measurements(submission)


    
            
            
    def finalize(self, cxn, context):
        self.excite.finalize(cxn, context)
        self.save_parameters(self.dv, cxn, self.cxnlab, self.spectrum_save_context)
        #pass

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
    exprt = setup_experiment(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
