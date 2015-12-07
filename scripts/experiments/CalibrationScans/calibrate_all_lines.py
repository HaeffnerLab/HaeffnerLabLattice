from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.spectrum import spectrum
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from fitters import peak_fitter
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad

class calibrate_all_lines(experiment):

    name = 'CalibAllLines'

    required_parameters = [('DriftTracker', 'line_selection_1'),
                           ('DriftTracker', 'line_selection_2'),
                           ]

    # parameters to overwrite
    remove_parameters = [
        ('Spectrum','ultimate'),
        ('Spectrum','custom'),
        ('Spectrum','manual_amplitude_729'),
        ('Spectrum','manual_excitation_time'),
        ('Spectrum','manual_scan'),
        ('Spectrum','scan_selection'),
        ('Spectrum','sensitivity_selection'),
        ('Spectrum','sideband_selection'),

        ('Display', 'relative_frequencies'),

        ('StateReadout', 'repeat_each_measurement'),]

        
        

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(spectrum.all_required_parameters()))
        parameters = list(parameters)
        for p in cls.remove_parameters:
            parameters.remove(p)
        #will be disabling sideband cooling automatically
        parameters.remove(('SidebandCooling','frequency_selection'))
        parameters.remove(('SidebandCooling','manual_frequency_729'))
        parameters.remove(('SidebandCooling','line_selection'))
        parameters.remove(('SidebandCooling','sideband_selection'))
        parameters.remove(('SidebandCooling','sideband_cooling_type'))
        parameters.remove(('SidebandCooling','sideband_cooling_cycles'))
        parameters.remove(('SidebandCooling','sideband_cooling_duration_729_increment_per_cycle'))
        parameters.remove(('SidebandCooling','sideband_cooling_frequency_854'))
        parameters.remove(('SidebandCooling','sideband_cooling_amplitude_854'))
        parameters.remove(('SidebandCooling','sideband_cooling_frequency_866'))
        parameters.remove(('SidebandCooling','sideband_cooling_amplitude_866'))
        parameters.remove(('SidebandCooling','sideband_cooling_amplitude_729'))
        parameters.remove(('SidebandCooling','sideband_cooling_optical_pumping_duration'))
        parameters.remove(('SidebandCoolingContinuous','sideband_cooling_continuous_duration'))
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729'))
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_cycles'))
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_repumps'))
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_additional_866'))
        parameters.remove(('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_between_pulses'))
    
    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.spectrum = self.make_experiment(spectrum)
        self.spectrum.initialize(cxn, context, ident)
        self.fitter = peak_fitter()
        self.pv = cxn.parametervault

        
    def run(self, cxn, context):
        
        dt = self.parameters.DriftTracker

        ### RUN THE FIRST CARRIER
        
        replace = TreeDict.fromdict({
            'Spectrum.line_selection':dt.line_selection_1,
            'Spectrum.scan_selection':'auto',
            'Spectrum.sensitivity_selection': 'fine',
            'Spectrum.sideband_selection':[0,0,0,0],
            'StatePreparation.sideband_cooling_enable':False,
            'StatePreparation.optical_pumping_enable':True,
            'Display.relative_frequencies':False,
            'StateReadout.repeat_each_measurement':100})

        self.spectrum.set_parameters(replace)
        self.spectrum.set_progress_limits(0, 25.0)
        
        fr, ex = self.spectrum.run(cxn, context)

        carr_1 = self.fitter.fit(fr, ex)
        carr_1 = WithUnit(carr_1, 'MHz')

        ### RUN THE SECOND CARRIER

        replace = TreeDict.fromdict({
            'Spectrum.line_selection':dt.line_selection_2,
            'Spectrum.scan_selection':'auto',
            'Spectrum.sensitivity_selection': 'fine',
            'Spectrum.sideband_selection':[0,0,0,0],
            'StatePreparation.sideband_cooling_enable':False,
            'StatePreparation.optical_pumping_enable':True,
            'Display.relative_frequencies':False,
            'StateReadout.repeat_each_measurement':100})

        self.spectrum.set_parameters(replace)
        self.spectrum.set_progress_limits(25.0, 50.0)
        
        fr, ex = self.spectrum.run(cxn, context)

        carr_2 = self.fitter.fit(fr, ex)
        carr_2 = WithUnit(carr_2, 'MHz')

        self.submit_dt(carr_1, dt.line_selection_1, carr_2, dt.line_selection_2)
        

        #### RUN THE FIRST SIDEBAND

        replace = TreeDict.fromdict({
            'Spectrum.line_selection':dt.line_selection_1,
            'Spectrum.scan_selection':'auto',
            'Spectrum.sensitivity_selection': 'normal',
            'Spectrum.sideband_selection':[-1,0,0,0],
            'StatePreparation.sideband_cooling_enable':False,
            'StatePreparation.optical_pumping_enable':True,
            'Display.relative_frequencies':True,
            'StateReadout.repeat_each_measurement':100})

        self.spectrum.set_parameters(replace)
        self.spectrum.set_progress_limits(50.0, 75.0)
        
        fr, ex = self.spectrum.run(cxn, context)

        sb_1 = self.fitter.fit(fr, ex)
        sb_1 = WithUnit(sb_1, 'MHz')

        #### SECOND SIDEBAND

        replace = TreeDict.fromdict({
            'Spectrum.line_selection':dt.line_selection_1,
            'Spectrum.scan_selection':'auto',
            'Spectrum.sensitivity_selection': 'normal',
            'Spectrum.sideband_selection':[0,-1,0,0],
            'StatePreparation.sideband_cooling_enable':False,
            'StatePreparation.optical_pumping_enable':True,
            'Display.relative_frequencies':True,
            'StateReadout.repeat_each_measurement':100})

        self.spectrum.set_parameters(replace)
        self.spectrum.set_progress_limits(75.0, 100.0)
        
        fr, ex = self.spectrum.run(cxn, context)

        sb_2 = self.fitter.fit(fr, ex)
        sb_2 = WithUnit(sb_2, 'MHz')

        self.submit_trap_frequencies(sb_1, sb_2)


    def submit_dt(self, f1, line1, f2, line2):
        submission = [
            (line1, f1), (line2, f2) ]

        self.drift_tracker.set_measurements(submission)

    def submit_trap_frequencies(self, f1, f2):
        self.pv.set_parameter('TrapFrequencies', 'radial_frequency_1', f1)
        self.pv.set_parameter('TrapFrequencies', 'radial_frequency_2', f2)

    def finalize(self, cxn, contest):
        self.spectrum.finalize(cxn, context)
