from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from OpticalPumpingContinuous import optical_pumping_continuous
from OpticalPumpingPulsed import optical_pumping_pulsed
from treedict import TreeDict

class optical_pumping(pulse_sequence):
    
    
    required_parameters = [
                  ('OpticalPumping','optical_pumping_type'),
                  ('OpticalPumping','optical_pumping_frequency_729'),
                  ('OpticalPumping','optical_pumping_frequency_854'),
                  ('OpticalPumping','optical_pumping_frequency_866'),
                  ('OpticalPumping','optical_pumping_amplitude_729'),
                  ('OpticalPumping','optical_pumping_amplitude_854'),
                  ('OpticalPumping','optical_pumping_amplitude_866')
                  ]
    
    required_subsequences = [optical_pumping_continuous, optical_pumping_pulsed]
    replaced_parameters = {
                           optical_pumping_continuous:[
                                                       ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_854'),
                                                       ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_854'),
                                                       ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_729'),
                                                       ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_729'),
                                                       ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_866'),
                                                       ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_866'),
                                                       ],
                           optical_pumping_pulsed:[
                                                     ('OpticalPumpingPulsed','optical_pumping_pulsed_frequency_854'),
                                                     ('OpticalPumpingPulsed','optical_pumping_pulsed_amplitude_854'),
                                                     ('OpticalPumpingPulsed','optical_pumping_pulsed_frequency_729'),
                                                     ('OpticalPumpingPulsed','optical_pumping_pulsed_amplitude_729'),
                                                     ('OpticalPumpingPulsed','optical_pumping_pulsed_frequency_866'),
                                                     ('OpticalPumpingPulsed','optical_pumping_pulsed_amplitude_866'),
                                                   ]
                           }
    
    def sequence(self):
        op = self.parameters.OpticalPumping
        
        if op.optical_pumping_type == 'continuous':
            continuous = True
        elif op.optical_pumping_type == 'pulsed':
            continuous = False
        else:
            raise Exception ('Incorrect optical pumping type {0}'.format(op.optical_pumping_type))
        if continuous:
            replace = {
                       'OpticalPumpingContinuous.optical_pumping_continuous_frequency_854':op.optical_pumping_frequency_854,
                       'OpticalPumpingContinuous.optical_pumping_continuous_amplitude_854':op.optical_pumping_amplitude_854,
                       'OpticalPumpingContinuous.optical_pumping_continuous_frequency_729':op.optical_pumping_frequency_729,
                       'OpticalPumpingContinuous.optical_pumping_continuous_amplitude_729':op.optical_pumping_amplitude_729,
                       'OpticalPumpingContinuous.optical_pumping_continuous_frequency_866':op.optical_pumping_frequency_866,
                       'OpticalPumpingContinuous.optical_pumping_continuous_amplitude_866':op.optical_pumping_amplitude_866,
                       }
            self.addSequence(optical_pumping_continuous, TreeDict.fromdict(replace))
        else:
            #pulsed
            replace = {
                       'OpticalPumpingPulsed.optical_pumping_pulsed_frequency_854':op.optical_pumping_frequency_854,
                       'OpticalPumpingPulsed.optical_pumping_pulsed_amplitude_854':op.optical_pumping_amplitude_854,
                       'OpticalPumpingPulsed.optical_pumping_pulsed_frequency_729':op.optical_pumping_frequency_729,
                       'OpticalPumpingPulsed.optical_pumping_pulsed_amplitude_729':op.optical_pumping_amplitude_729,
                       'OpticalPumpingPulsed.optical_pumping_pulsed_frequency_866':op.optical_pumping_frequency_866,
                       'OpticalPumpingPulsed.optical_pumping_pulsed_amplitude_866':op.optical_pumping_amplitude_866,
                       }
            self.addSequence(optical_pumping_pulsed, TreeDict.fromdict(replace))