from common.abstractdevices.script_scanner.scan_methods import experiment
from excitation_729 import excitation_729
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class spectrum(experiment):
    
    name = 'Spectrum729'
    required_parameters = [
                           ('Spectrum','custom'),
                           ('Spectrum','fine'),
                           ('Spectrum','line_selection'),
                           ('Spectrum','manual_amplitude_729'),
                           ('Spectrum','manual_excitation_time'),
                           ('Spectrum','manual_scan'),
                           ('Spectrum','normal'),
                           ('Spectrum','scan_selection'),
                           ('Spectrum','sensitivity_selection'),
                           ('Spectrum','sideband_selection'),
                           ('Spectrum','ultimate'),
                           
                           ('TrapFrequencies','axial_frequency'),
                           ('TrapFrequencies','radial_frequency_1'),
                           ('TrapFrequencies','radial_frequency_2'),
                           ('TrapFrequencies','rf_drive_frequency'),
                           ]
    
    optional_parmeters = [
                          ('Spectrum', 'window_name')
                          ]
    required_parameters.extend(excitation_729.required_parameters)
    #removing parameters we'll be overwriting, and they do not need to be loaded
    required_parameters.remove(('Excitation_729','rabi_excitation_amplitude'))
    required_parameters.remove(('Excitation_729','rabi_excitation_duration'))
    required_parameters.remove(('Excitation_729','rabi_excitation_frequency'))
    
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.excite = self.make_experiment(excitation_729)
        self.excite.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.spectrum_save_context = cxn.context()
        self.setup_data_vault()
    
    def setup_sequence_parameters(self):
        sp = self.parameters.Spectrum
        if sp.scan_selection == 'manual':
            minim,maxim,steps = sp.manual_scan
            duration = sp.manual_excitation_time
            amplitude = sp.manual_amplitude_729
        elif sp.scan_selection == 'auto':
            center_frequency = cm.frequency_from_line_selection(sp.scan_selection, None , sp.line_selection, self.drift_tracker)
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
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'MHz') for pt in self.scan]
        
    def setup_data_vault(self):
        localtime = time.localtime()
        datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        directory = ['','Experiments']
        directory.extend(self.name)
        directory.extend(dirappend)
        self.dv.cd(directory ,True, context = self.spectrum_save_context)
        self.dv.new('Spectrum {}'.format(datasetNameAppend),[('Freq', 'MHz')],[('Excitation Probability','Arb','Arb')], context = self.spectrum_save_context)
        window_name = self.parameters.get('Spectrum.window_name', ['Spectrum'])
        self.dv.add_parameter('Window', window_name, context = self.spectrum_save_context)
        self.dv.add_parameter('plotLive', True, context = self.spectrum_save_context)
        
    def run(self, cxn, context):
        self.setup_sequence_parameters()
        for i,freq in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            self.parameters['Excitation_729.rabi_excitation_frequency'] = freq
            self.excite.set_parameters(self.parameters)
            excitation = self.excite.run(cxn, context)
            self.dv.add((freq, excitation), context = self.spectrum_save_context)
            self.update_progress(i)
     
    def finalize(self, cxn, context):
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
    exprt = spectrum(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)