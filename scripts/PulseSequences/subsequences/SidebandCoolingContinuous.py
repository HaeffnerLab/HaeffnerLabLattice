from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from OpticalPumpingContinuous import optical_pumping_continuous
from treedict import TreeDict

class sideband_cooling_continuous(pulse_sequence):

    required_parameters = [
                           ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'),
                           ('SidebandCoolingContinuous','sideband_cooling_continuous_frequency_854'),
                           ('SidebandCoolingContinuous','sideband_cooling_conitnuous_amplitude_854'),
                           ('SidebandCoolingContinuous','sideband_cooling_continuous_frequency_729'),
                           ('SidebandCoolingContinuous','sideband_cooling_continuous_amplitude_729'),
                           ('SidebandCoolingContinuous','sideband_cooling_continuous_frequency_866'),
                           ('SidebandCoolingContinuous','sideband_cooling_continuous_amplitude_866'),
                           ]
    
    required_subsequences = [optical_pumping_continuous]
    
    def sequence(self):
        replace = self.make_replace()
        self.addSequence(optical_pumping_continuous, TreeDict.fromdict(replace))

    def make_replace(self):
        sc = self.parameters.SidebandCoolingContinuous
        replace = {
                   'OpticalPumpingContinuous.optical_pumping_continuous_duration': sc.sideband_cooling_continuous_duration,
                   'OpticalPumpingContinuous.optical_pumping_continuous_frequency_854':sc.sideband_cooling_continuous_frequency_854,
                   'OpticalPumpingContinuous.optical_pumping_continuous_amplitude_854':sc.sideband_cooling_conitnuous_amplitude_854,
                   'OpticalPumpingContinuous.optical_pumping_continuous_frequency_729':sc.sideband_cooling_continuous_frequency_729,
                   'OpticalPumpingContinuous.optical_pumping_continuous_amplitude_729':sc.sideband_cooling_continuous_amplitude_729,
                   'OpticalPumpingContinuous.optical_pumping_continuous_frequency_866':sc.sideband_cooling_continuous_frequency_866, 
                   'OpticalPumpingContinuous.optical_pumping_continuous_amplitude_866':sc.sideband_cooling_continuous_amplitude_866,
                   }
        return replace