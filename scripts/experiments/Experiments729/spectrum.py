from common.abstractdevices.script_scanner.scan_methods import experiment
from excitations import excitation_729
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
import lattice.scripts.scriptLibrary.scan_methods as sm
from lattice.scripts.scriptLibrary import dvParameters
from lattice.scripts.experiments.Crystallization.crystallization import crystallization
import time
import labrad
from labrad.units import WithUnit
import numpy as np

class spectrum(experiment):
    
    name = 'Spectrum729'
    spectrum_required_parameters = [
                           ('Spectrum','custom'),
                           ('Spectrum','normal'),
                           ('Spectrum','fine'),
                           ('Spectrum','ultimate'),
                           ('Spectrum','car1_sensitivity'),
                           ('Spectrum','car2_sensitivity'),
                           
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

                           ('Display', 'relative_frequencies'),                           ]
    
    spectrum_optional_parmeters = [
                          ('Spectrum', 'window_name')
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
    
    def initialize(self, cxn, context, ident, use_camera_override=None):
        self.ident = ident
        self.excite = self.make_experiment(excitation_729)
        self.excite.initialize(cxn, context, ident, use_camera_override)
        if self.parameters.Crystallization.auto_crystallization:
            self.crystallizer = self.make_experiment(crystallization)
            self.crystallizer.initialize(cxn, context, ident)
        self.scan = []
        self.amplitude = None
        self.duration = None
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.save_context = cxn.context()
        try:
            self.grapher = cxn.grapher
        except: self.grapher = None
        self.cxn = cxn
        
    def setup_sequence_parameters(self):
        sp = self.parameters.Spectrum
        if sp.scan_selection == 'manual':
            center_frequency = sp.manual_frequency
            self.carrier_frequency = WithUnit(0.0, 'MHz')
        else:
            center_frequency = sm.compute_frequency_729(sp.line_selection, sp.sideband_selection, self.parameters.TrapFrequencies, self.drift_tracker)
            self.carrier_frequency = sm.compute_carrier_frequency(sp.line_selection, self.drift_tracker)

        span, resolution, duration, amplitude = sp[sp.sensitivity_selection]
        minim = center_frequency - span / 2.0
        maxim = center_frequency + span / 2.0
        steps = int(span / resolution )
        #making the scan
        self.parameters['Excitation_729.rabi_excitation_duration'] = duration
        self.parameters['Excitation_729.rabi_excitation_amplitude'] = amplitude
        minim = minim['MHz']; maxim = maxim['MHz']
        self.scan = np.linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'MHz') for pt in self.scan]

    def run(self, cxn, context):
        self.setup_sequence_parameters()

        if self.parameters.Display.relative_frequencies:
            sc =[x - self.carrier_frequency for x in self.scan]
        else: sc = self.scan

        dv_args = {
            'pulse_sequence': 'spectrum_rabi',
            'parameter':'Excitation_729.rabi_excitaton_frequency',
            'headings': ['Ion {}'.format(ion) for ion in range(self.excite.output_size)],
            'window_name':'spectrum',
            'axis': sc
                }
        sm.setup_data_vault(cxn, self.save_context, dv_args)

        fr = []
        exci = []
        
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
            self.dv.add(submission, context = self.save_context)
            self.update_progress(i)
            fr.append(submission[0])
            exci.append(excitation)

        return fr, exci
    
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
        #self.save_parameters(self.dv, cxn, self.cxnlab, self.spectrum_save_context)

    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)

    def save_parameters(self, dv, cxn, context):
        measuredDict = dvParameters.measureParameters(cxn)
        dvParameters.saveParameters(dv, measuredDict, context)
        dvParameters.saveParameters(dv, dict(self.parameters), context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = spectrum(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
