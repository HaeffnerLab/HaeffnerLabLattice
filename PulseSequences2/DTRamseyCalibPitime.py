from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np
from RabiFlopping import RabiFlopping

#class RabiFloppingMulti(pulse_sequence):
#    is_multi = True
#    sequences = [RabiFlopping, Spectrum]

class RabiLine1(RabiFlopping):

    scannable_params = {
        'RabiFlopping.duration':  [(0., 15., 3, 'us'), 'rabi']
        #'Excitation_729.rabi_excitation_duration' : [(-150, 150, 10, 'kHz'),'spectrum'],
              }

    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)

        data = data.mean(axis=1)
        for i, p in enumerate(data):
            if p > 0.5:
                ind1 = i-1
                ind2 = i
                p1 = data[ind1]
                p2 = data[ind2]
                x1 = x[ind1]
                x2 = x[ind2]
                break

        pi_time = (x1 + (0.5 - p1)*(x2-x1)/(p2-p1)) * 2
        pi_time = U(pi_time, 'us')
        print "line_1_pi_time = ", pi_time
        cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'line_1_pi_time', pi_time)
        return pi_time

class RabiLine2(RabiFlopping):

    scannable_params = {
        'RabiFlopping.duration':  [(0., 15., 3, 'us'), 'rabi']
        #'Excitation_729.rabi_excitation_duration' : [(-150, 150, 10, 'kHz'),'spectrum'],
              }

    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)

    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)

        data = data.mean(axis=1)
        for i, p in enumerate(data):
            if p > 0.5:
                ind1 = i-1
                ind2 = i
                p1 = data[ind1]
                p2 = data[ind2]
                x1 = x[ind1]
                x2 = x[ind2]
                break

        pi_time = (x1 + (0.5 - p1)*(x2-x1)/(p2-p1)) * 2
        pi_time = U(pi_time, 'us')
        print "line_2_pi_time = ", pi_time
        cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'line_2_pi_time', pi_time)
        return pi_time

class DTRamseyCalibPitime(pulse_sequence):

    show_params = ['DriftTrackerRamsey.line_1_amplitude',
                  'DriftTrackerRamsey.line_1_pi_time',
                  'DriftTrackerRamsey.line_2_amplitude',
                  'DriftTrackerRamsey.line_2_pi_time',
                  'DriftTracker.line_selection_1',
                  'DriftTracker.line_selection_2',
                  'DriftTrackerRamsey.gap_time_1',
                  'DriftTrackerRamsey.gap_time_2',
                  'DriftTrackerRamsey.submit',
                  'DriftTrackerRamsey.bfield_difference_2ions',
                  'DriftTrackerRamsey.no_of_readout_ion_2ions']

    sequence = [(RabiLine1, {'RabiFlopping.line_selection': 'DriftTracker.line_selection_1',
                            'RabiFlopping.rabi_amplitude_729': 'DriftTrackerRamsey.line_1_amplitude',
                            'RabiFlopping.order': 0,
                            'StatePreparation.aux_optical_pumping_enable': False,
                            'StatePreparation.sideband_cooling_enable': True,
                            'Excitation_729.channel_729': "729global",
                            'StatePreparation.channel_729': "729global",
                            'SidebandCooling.selection_sideband': "axial_frequency"}),
                (RabiLine2, {'RabiFlopping.line_selection': 'DriftTracker.line_selection_2',
                            'RabiFlopping.rabi_amplitude_729': 'DriftTrackerRamsey.line_2_amplitude',
                            'RabiFlopping.order': 0,
                            'StatePreparation.aux_optical_pumping_enable': False,
                            'StatePreparation.sideband_cooling_enable': True,
                            'Excitation_729.channel_729': "729global",
                            'StatePreparation.channel_729': "729global",
                            'SidebandCooling.selection_sideband': "axial_frequency"})]