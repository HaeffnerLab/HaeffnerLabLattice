from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_729
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
import numpy as np

class take_spectrum_to_fit(experiment):
    
    name = 'Z_Take_Spectrum_to_Fit'
    take_spectrum_to_fit_required_parameters = [
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
                           
                           ('Display', 'relative_frequencies'),    
                           ]
    
    spectrum_optional_parmeters = [
                          ('Spectrum', 'window_name')
                          ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.take_spectrum_to_fit_required_parameters)
        parameters = parameters.union(set(excitation_729.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Excitation_729','rabi_excitation_amplitude'))
        parameters.remove(('Excitation_729','rabi_excitation_duration'))
        parameters.remove(('Excitation_729','rabi_excitation_frequency'))
        return parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation_729)
        self.excite.initialize(cxn, context, ident)
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker

        try:
            self.grapher = cxn.grapher
        except: self.grapher = None
        
        self.fitter = cxn.fitter

        self.dv = cxn.data_vault
        self.spectrum_save_context = cxn.context()
    
    def setup_sequence_parameters(self):
        sp = self.parameters.Spectrum
        if sp.scan_selection == 'manual':
            minim,maxim,steps = sp.manual_scan
            duration = sp.manual_excitation_time
            amplitude = sp.manual_amplitude_729
            self.carrier_frequency = WithUnit(0.0, 'MHz')
        elif sp.scan_selection == 'auto':
            center_frequency = cm.frequency_from_line_selection(sp.scan_selection, None , sp.line_selection, self.drift_tracker)
            self.carrier_frequency = center_frequency
            center_frequency = cm.add_sidebands(center_frequency, sp.sideband_selection, self.parameters.TrapFrequencies)
            span, resolution, duration, amplitude = sp[sp.sensitivity_selection]
            minim = center_frequency - span / 2.0
            maxim = center_frequency + span / 2.0
            steps = int(span / resolution )
        else:
            raise Exception("Incorrect Spectrum Scan Type")
        #making the scan
        self.parameters['Excitation_729.rabi_excitation_duration'] = duration
        self.parameters['Excitation_729.rabi_excitation_amplitude'] = amplitude
        minim = minim['MHz']; maxim = maxim['MHz']
        self.scan = np.linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'MHz') for pt in self.scan]                       
        
    def setup_data_vault(self):       	                           
        
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend([self.name])
        directory.extend(dirappend)
        
        self.directory_for_fitter = directory
        
        self.dv.cd(directory ,True, context = self.spectrum_save_context)
        output_size = self.excite.output_size
        dependants = [('Excitation','Ion {}'.format(ion),'Probability') for ion in range(output_size)]

        ds = self.dv.new('Spectrum {}'.format(datasetNameAppend),[('Excitation', 'us')], dependants , context = self.spectrum_save_context)
        window_name = self.parameters.get('Spectrum.window_name', ['spectrum'])[0]
        #window_name = self.get_window_name()
        self.dv.add_parameter('Window', [window_name], context = self.spectrum_save_context)
        #self.dv.add_parameter('plotLive', False, context = self.spectrum_save_context)
        #self.save_parameters(self.dv, self.cxn, self.cxnlab, self.spectrum_save_context)
        sc = []
        if self.parameters.Display.relative_frequencies:
            sc =[x - self.carrier_frequency for x in self.scan]
        else: sc = self.scan
        if self.grapher is not None:
            self.grapher.plot_with_axis(ds, window_name, sc, False)
        
    
    def run(self, cxn, context):
        
        self.setup_sequence_parameters()
        self.setup_data_vault()
              
        
        #    fr.append(submission[0])
        #    exci.append(excitation)
            
        ################
        excitation_arr = []
        
        for i,freq in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            excitation = self.get_excitation_crystallizing(cxn, context, freq)
            if excitation is None: break
            if self.parameters.Display.relative_frequencies:
                submission = [freq['MHz'] - self.carrier_frequency['MHz']]
            else:
                submission = [freq['MHz']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.spectrum_save_context)
            self.update_progress(i)
            
            excitation_arr.append(excitation[0])
    
        if not should_stop:
            fitted_frequency = self.fit_center_freq(cxn, context)
        else:
            fitted_frequency = 0.0
                
        return fitted_frequency    
        
            
    
    def get_excitation_crystallizing(self, cxn, context, freq):
        excitation = self.do_get_excitation(cxn, context, freq)
        if self.parameters.Crystallization.auto_crystallization:
            initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
            #if initially melted, redo the point
            while initally_melted:
                if not got_crystallized:
                    #if crystallizer wasn't able to crystallize, then pause and wait for user interaction
                    self.cxn.scriptscanner.pause_script(self.ident, True)
                    should_stop = self.pause_or_stop()
                    if should_stop: return None
                excitation = self.do_get_excitation(cxn, context, freq)
                initally_melted, got_crystallized = self.crystallizer.run(cxn, context)
        return excitation
    
    def do_get_excitation(self, cxn, context, freq):
        self.parameters['Excitation_729.rabi_excitation_frequency'] = freq
        self.excite.set_parameters(self.parameters)
        excitation, readouts = self.excite.run(cxn, context)
        return excitation
    
    def fit_lorentzian(self, timeout):
        #for lorentzian format is FWHM, center, height, offset
        scan = np.array([pt['MHz'] for pt in self.scan])
        
        fwhm_guess = (scan.max() - scan.min()) / 10.0
        center_guess = np.average(scan)
        self.dv.add_parameter('Fit', ['0', 'Lorentzian', '[{0}, {1}, {2}, {3}]'
                                      .format(fwhm_guess, center_guess, 0.5, 0.0)], context = self.spectrum_save_context)
        submitted = self.cxn.data_vault.wait_for_parameter('Accept-0', timeout, context = self.spectrum_save_context)
        if submitted:
            return self.cxn.data_vault.get_parameter('Solutions-0-Lorentzian', context = self.spectrum_save_context)
        else:
            return None
        
    def fit_center_freq(self, cxn, context):
        directory = (self.directory_for_fitter,1)
        self.fitter.load_data(directory)
        self.fitter.fit('Lorentzian', True)
        accepted = self.fitter.wait_for_acceptance()
        if accepted:
            fitted_freq = self.fitter.get_parameter('Center')
            #print fitted_freq
            result = WithUnit(fitted_freq,'MHz')
            
            #self.pv.set_parameter('TrapFrequencies',self.sideband_selection,result)
            print "fit accepted"
            #print time.time(), result
            #data_time = datetime.datetime.now().hour*3600+datetime.datetime.now().minute*60+datetime.datetime.now().second
            #self.dv.add([data_time, result['MHz']],context=self.save_trap_freq)
            
            return fitted_freq
        else:
            print 'fit rejected!'
            return None    
        
    def finalize(self, cxn, context):
        self.excite.finalize(cxn, context)
        self.save_parameters(self.dv, cxn, self.cxnlab, self.spectrum_save_context)

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
    exprt = take_spectrum_to_fit(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
