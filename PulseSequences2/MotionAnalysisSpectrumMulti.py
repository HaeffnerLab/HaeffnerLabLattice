from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from lattice.scripts.scriptLibrary.devices import agilent
import time
from treedict import TreeDict
import numpy as np
from MotionAnalysisSpectrum import MotionAnalysisSpectrum

#from subsequences.GlobalRotation import GlobalRotation
#from subsequences.LocalRotation import LocalRotation
#from subsequences.TurnOffAll import TurnOffAll

class MotionAnalysisSpectrum1(MotionAnalysisSpectrum):
    scannable_params = {'Motion_Analysis.detuning': [(-7.0,7.0, 0.75, 'kHz'),'radial1']} 

class MotionAnalysisSpectrum2(MotionAnalysisSpectrum):
    scannable_params = {'Motion_Analysis.detuning': [(-7.0,7.0, 0.75, 'kHz'),'radial2']}

class MotionAnalysisSpectrumMulti(pulse_sequence):
    is_composite = True
    # at the moment fixed params are shared between the sub sequence!!! 
    fixed_params = {#'opticalPumping.line_selection': 'S-1/2D+3/2',
                    'Display.relative_frequencies': True,
                    'StatePreparation.aux_optical_pumping_enable': False,
                    'StatePreparation.sideband_cooling_enable': True,
                    'StateReadout.readout_mode': "pmt"}

                    
    sequences = [(MotionAnalysisSpectrum1, {'Motion_Analysis.sideband_selection': 'radial_frequency_1',
                    'RabiFlopping.selection_sideband': 'radial_frequency_1'}),
                 (MotionAnalysisSpectrum2, {'Motion_Analysis.sideband_selection': 'radial_frequency_2',
                    'RabiFlopping.selection_sideband': 'radial_frequency_2'})] 

    show_params= ['Motion_Analysis.pulse_width_397',
                  'Motion_Analysis.amplitude_397',
                  'Motion_Analysis.sideband_selection',

                  'RabiFlopping.duration',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',]