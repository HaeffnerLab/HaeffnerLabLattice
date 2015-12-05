from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.experiments.Experiments729.spectrum import spectrum
from lattice.scripts.scriptLibrary import scan_methods
from lattice.scripts.scriptLibrary import dvParameters
from pi_time_fitter import pi_time_fitter
from labrad.units import WithUnit
from treedict import TreeDict
import numpy as np
import labrad

class calibrate_all_lines(experiment):

    name = 'CalibAllLines'

    required_parameters = [()]

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

        ('Display', 'relative_frequencies')]

        
        

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
   
