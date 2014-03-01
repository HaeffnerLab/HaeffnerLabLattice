from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_729
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
import numpy as np

class Sideband_tracker(experiment):
    
    name = 'Sideband_tracker'
    spectrum_required_parameters = [
                           
                           ('Sideband_tracker','line_selection'),
                           ('Sideband_tracker','sensitivity'),
                           ('Sideband_tracker','sideband_selection'),
                           ('Sideband_tracker','ion_selection'),
                           ('Sideband_tracker','auto_fit'),

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
                          ('Sideband_tracker', 'window_name')
                          ]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.spectrum_required_parameters)
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
        self.dv = cxn.data_vault
        self.fitter = cxn.fitter
        self.pv = cxn.parametervault
        self.spectrum_save_context = cxn.context()
        self.save_trap_freq = cxn.context()
        self.ion_number = int(self.parameters.Sideband_tracker.ion_selection)
        self.sideband_selection = cm.selected_sideband(self.parameters.Sideband_tracker.sideband_selection)
        self.auto_fit = self.parameters.Sideband_tracker.auto_fit
        print self.sideband_selection
    
    def setup_sequence_parameters(self):
        sp = self.parameters.Sideband_tracker
        center_frequency = cm.frequency_from_line_selection('auto', None , sp.line_selection, self.drift_tracker)
        self.carrier_frequency = center_frequency
        center_frequency = cm.add_sidebands(center_frequency, sp.sideband_selection, self.parameters.TrapFrequencies)
        span, resolution, duration, amplitude = sp['sensitivity']
        minim = center_frequency - span / 2.0
        maxim = center_frequency + span / 2.0
        steps = int(span / resolution )
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
        dependants = [('Excitation','Ion {}'.format(self.ion_number),'Probability')]
        self.dv.new('Spectrum {}'.format(datasetNameAppend),[('Excitation', 'us')], dependants , context = self.spectrum_save_context)
        window_name = self.parameters.get('Spectrum.window_name', ['Spectrum'])
        self.dv.add_parameter('Window', window_name, context = self.spectrum_save_context)
        self.dv.add_parameter('plotLive', True, context = self.spectrum_save_context)
        ##### save result for long term tracking ####
        directory_trap = ['','Drift_Tracking','Trap_frequencies']
        directory_trap.append(time.strftime("%Y%b%d",localtime))
        self.dv.cd(directory_trap ,True, context = self.save_trap_freq)
        datasetnametrap = self.sideband_selection
        datasetstrap_in_folder = self.dv.dir(context=self.save_trap_freq)[1]
        names = sorted([name for name in datasetstrap_in_folder if datasetnametrap in name])
        if names:
            #dataset with that name exist
            self.dv.open_appendable(names[0],context=self.save_trap_freq)
        else:
            #dataset doesn't already exist
            self.dv.new(datasetnametrap,[('Time', 'Sec')],[('Trap_frequency','MHz','Frequency')],context=self.save_trap_freq)
            window_name = [self.sideband_selection]
            self.dv.add_parameter('Window', window_name,context=self.save_trap_freq)
            self.dv.add_parameter('plotLive', True,context=self.save_trap_freq)
        
    def run(self, cxn, context):
        self.setup_data_vault()
        self.setup_sequence_parameters()
        for i,freq in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            ## get only the ion that we want
            excitation_all = self.get_excitation_crystallizing(cxn, context, freq)
            if excitation_all is None: break
            excitation = np.array([excitation_all[self.ion_number]])
            print excitation
            submission = [freq['MHz']]
            submission.extend(excitation)
            self.dv.add(submission, context = self.spectrum_save_context)
            self.update_progress(i)
        ### don't fit if stop ###
        if not should_stop:
            self.fit_center_freq(cxn, context)
    
    def fit_center_freq(self, cxn, context):
        directory = (self.directory_for_fitter,1)
        self.fitter.load_data(directory)
        self.fitter.fit('Lorentzian', self.auto_fit)
        accepted = self.fitter.wait_for_acceptance()
        if accepted:
            fitted_freq = self.fitter.get_parameter('Center')
            print fitted_freq
            result = WithUnit(np.abs(fitted_freq - self.carrier_frequency),'MHz')
            self.pv.set_parameter('TrapFrequencies',self.sideband_selection,result)
            print "fit accepted"
            print time.time(), result
            self.dv.add([time.time(), result['MHz']],context=self.save_trap_freq)
        else:
            print 'fit rejected!'
        
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
    exprt = Sideband_tracker(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)