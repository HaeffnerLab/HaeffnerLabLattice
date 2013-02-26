from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from OpticalPumpingPulsed import optical_pumping_pulsed
from treedict import TreeDict

class sideband_cooling_pulsed(pulse_sequence):
    
    required_parameters = [
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_cycles'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_repumps'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_additional_866'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_between_pulses'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_frequency_854'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_amplitude_854'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_frequency_729'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_amplitude_729'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_frequency_866'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_amplitude_866'),
                           ]
    
    required_subsequences = [optical_pumping_pulsed]
    
    def sequence(self):
        replace = self.make_replace()
        self.addSequence(optical_pumping_pulsed, TreeDict.fromdict(replace))
    
    def make_replace(self):
        scp = self.parameters.SidebandCoolingPulsed
        replace = {
                   'OpticalPumpingPulsed.optical_pumping_pulsed_cycles':scp.sideband_cooling_pulsed_cycles,
                   'OpticalPumpingPulsed.optical_pumping_pulsed_duration_729': scp.sideband_cooling_pulsed_duration_729,
                   'OpticalPumpingPulsed.optical_pumping_pulsed_duration_repumps': scp.sideband_cooling_pulsed_duration_repumps,
                   'OpticalPumpingPulsed.optical_pumping_pulsed_duration_additional_866': scp.sideband_cooling_pulsed_duration_additional_866,
                   'OpticalPumpingPulsed.optical_pumping_pulsed_duration_between_pulses': scp.sideband_cooling_pulsed_duration_between_pulses,
                   'OpticalPumpingPulsed.optical_pumping_pulsed_frequency_854':scp.sideband_cooling_pulsed_frequency_854,
                   'OpticalPumpingPulsed.optical_pumping_pulsed_amplitude_854':scp.sideband_cooling_pulsed_amplitude_854,
                   'OpticalPumpingPulsed.optical_pumping_pulsed_frequency_729':scp.sideband_cooling_pulsed_frequency_729,
                   'OpticalPumpingPulsed.optical_pumping_pulsed_amplitude_729':scp.sideband_cooling_pulsed_amplitude_729,
                   'OpticalPumpingPulsed.optical_pumping_pulsed_frequency_866':scp.sideband_cooling_pulsed_frequency_866,
                   'OpticalPumpingPulsed.optical_pumping_pulsed_amplitude_866':scp.sideband_cooling_pulsed_amplitude_866,
                  }
        return replace