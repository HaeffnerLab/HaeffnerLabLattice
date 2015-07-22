from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class vaet(pulse_sequence):

    required_parameters = [
        ('VAET', 'frequency'),
        ('VAET', 'duration'),
        ('VAET', 'pi_time'),
        ('VAET', 'car_amplitude'),
        ('VAET', 'shape_profile'),

        ('MolmerSorensen', 'amplitude'),
        ('SZX', 'amplitude')
        ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        slope_dict = {0:0.0, 2:2.0, 4:5.0, 6:30.0}
        #p = self.parameters.MolmerSorensen
        v = self.parameters.VAET
        ms = self.parameters.MolmerSorensen
        szx = self.parameters.SZX
        duration = v.duration
        print duration
        frequency = v.frequency
        frequency_advance_duration = WithUnit(6, 'us')
        phase = WithUnit(0, 'deg')
        try:
            slope_duration = WithUnit(int(slope_dict[v.shape_profile]),'us')
        except KeyError:
            raise Exception('Cannot find shape profile: ' + str(v.shape_profile))
        ampl_off = WithUnit(-63.0, 'dBm')
    
        self.addDDS('729DP', self.start, frequency_advance_duration, frequency, ampl_off)
        self.addDDS('729DP_1', self.start, frequency_advance_duration, frequency, ampl_off)

        ##### PI PULSE ON THE CARRIER #######
        self.addDDS('729DP_1', self.start + frequency_advance_duration, v.pi_time, frequency, v.car_amplitude, phase)

        st = self.start + frequency_advance_duration + v.pi_time

        #### MOLMER SORENSEN INTERATION ###
        self.addDDS('729DP', st + frequency_advance_duration, duration, frequency, ms.amplitude, phase, profile=int(v.shape_profile))
        self.addTTL('bichromatic_1', st, duration + 2*frequency_advance_duration + slope_duration)
        ###### SZX INTERACTION #######
        self.addDDS('729DP_1', st + frequency_advance_duration, duration, frequency, szx.amplitude, phase,profile=int(v.shape_profile))
        self.addTTL('bichromatic_2', st, duration + 2*frequency_advance_duration + slope_duration)
        
        self.end = st + duration+ 2*frequency_advance_duration + slope_duration
