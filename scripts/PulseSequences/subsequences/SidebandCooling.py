from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from OpticalPumping import optical_pumping
from SidebandCoolingContinuous import sideband_cooling_continuous
from SidebandCoolingPulsed import sideband_cooling_pulsed
from treedict import TreeDict

class sideband_cooling(pulse_sequence):
    
    required_parameters = [
                           ('SidebandCooling','sideband_cooling_cycles'),
                           ('SidebandCooling','sideband_cooling_type'),
                           ('SidebandCooling','sideband_cooling_duration_729_increment_per_cycle'),
                           ('SidebandCooling','sideband_cooling_optical_pumping_duration'),
                           ('SidebandCooling','sideband_cooling_amplitude_866'),
                           ('SidebandCooling','sideband_cooling_amplitude_854'),
                           ('SidebandCooling','sideband_cooling_amplitude_729'),
                           ('SidebandCooling','sideband_cooling_frequency_854'),
                           ('SidebandCooling', 'sideband_cooling_frequency_866'),
                           ('SidebandCooling', 'sideband_cooling_frequency_729'),
                           ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'),
                           ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729'),
                           ]
    
    required_subsequences = [sideband_cooling_continuous, sideband_cooling_pulsed, optical_pumping]
    
    def sequence(self):
        '''
        sideband cooling pulse sequence consists of multiple sideband_cooling_cycles where each cycle consists 
        of a period of sideband cooling followed by continuous optical pumping. 
        
        sideband cooling can be either pulsed or continuous 
        '''
        sc = self.parameters.SidebandCooling
        if sc.sideband_cooling_type == 'continuous':
            continuous = True
        elif sc.sideband_cooling_type == 'pulsed':
            continuous = False
        else:
            raise Exception ("Incorrect Sideband cooling type {0}".format(sc.sideband_cooling_type))
        
        if continuous:
            cooling = sideband_cooling_continuous
            duration_key = 'SidebandCoolingContinuous.sideband_cooling_continuous_duration'
            cooling_replace = {
                               'SidebandCoolingContinuous.sideband_cooling_continuous_duration':self.parameters.SidebandCoolingContinuous.sideband_cooling_continuous_duration,
                               'SidebandCoolingContinuous.sideband_cooling_continuous_frequency_854':sc.sideband_cooling_frequency_854,
                               'SidebandCoolingContinuous.sideband_cooling_continuous_frequency_729':sc.sideband_cooling_frequency_729,
                               'SidebandCoolingContinuous.sideband_cooling_continuous_frequency_866':sc.sideband_cooling_frequency_866,
                               'SidebandCoolingContinuous.sideband_cooling_conitnuous_amplitude_854':sc.sideband_cooling_amplitude_854,
                               'SidebandCoolingContinuous.sideband_cooling_continuous_amplitude_729':sc.sideband_cooling_amplitude_729,
                               'SidebandCoolingContinuous.sideband_cooling_continuous_amplitude_866':sc.sideband_cooling_amplitude_866,
                               }
        else:
            #pulsed
            cooling = sideband_cooling_pulsed
            duration_key = 'SidebandCoolingPulsed.sideband_cooling_pulsed_duration_729'
            cooling_replace = {
                                'SidebandCoolingPulsed.sideband_cooling_pulsed_duration_729':self.parameters.SidebandCoolingPulsed.sideband_cooling_pulsed_duration_729,
                                'SidebandCoolingPulsed.sideband_cooling_pulsed_frequency_854':sc.sideband_cooling_frequency_854,
                                'SidebandCoolingPulsed.sideband_cooling_pulsed_amplitude_854':sc.sideband_cooling_amplitude_854,
                                'SidebandCoolingPulsed.sideband_cooling_pulsed_frequency_729':sc.sideband_cooling_frequency_729,
                                'SidebandCoolingPulsed.sideband_cooling_pulsed_amplitude_729':sc.sideband_cooling_amplitude_729,
                                'SidebandCoolingPulsed.sideband_cooling_pulsed_frequency_866':sc.sideband_cooling_frequency_866,
                                'SidebandCoolingPulsed.sideband_cooling_pulsed_amplitude_866':sc.sideband_cooling_amplitude_866,
                               }
        optical_pump_replace = {
                                'OpticalPumping.optical_pumping_continuous':True,
                                'OpticalPumpingContinuous.optical_pumping_continuous_duration':sc.sideband_cooling_optical_pumping_duration,
                                }
        for i in range(int(sc.sideband_cooling_cycles)):
            #each cycle, increment the 729 duration
            cooling_replace[duration_key] +=  sc.sideband_cooling_duration_729_increment_per_cycle
            self.addSequence(cooling, TreeDict.fromdict(cooling_replace))
            self.addSequence(optical_pumping, TreeDict.fromdict(optical_pump_replace))