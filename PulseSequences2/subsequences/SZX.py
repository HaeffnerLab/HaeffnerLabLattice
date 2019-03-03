from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class SZX(pulse_sequence):
    
    
    def sequence(self):

        p = self.parameters.SZX
        amp = p.amplitude
        duration = p.duration
        bichros = p.bichro_enable
        freq = p.frequency
        phase = p.phase

        frequency_advance_duration = U(6., "us")
        ampl_off = U(-63., "dBm")
        shape_profile = 2
        slope_duration = U(2., "us")

        self.end = self.start + 3 * frequency_advance_duration + duration + slope_duration
        
        #  First advance the frequency, but keep amplitude low.
        self.addDDS("729local", self.start, frequency_advance_duration, freq, ampl_off)
        # self.addDDS('729global', self.start , duration+ frequency_advance_duration, U(220.0, 'MHz'), ampl_off)
       
        #  Making sure that the global is off -> enabling the turned off sp and detuing the beam
        if bichros:
            self.addTTL("bichromatic_2", self.start, duration + 2 * frequency_advance_duration + slope_duration)
        

        self.addDDS("729local", self.start + frequency_advance_duration, duration, freq, amp, phase, 
                    profile=shape_profile)


        # tunning DP off gradually             
        #self.addDDS("729global", self.start + duration + 2 * frequency_advance_duration + slope_duration, 
        #            frequency_advance_duration, frequency, ampl_off)
        self.addDDS("729local", self.start + duration + 2 * frequency_advance_duration + slope_duration, 
                    frequency_advance_duration, freq, ampl_off)
        # self.addDDS('729global', self.start + duration + 2 * frequency_advance_duration + slope_duration, 
        #             frequency_advance_duration, U(220., "MHz"), ampl_off)        
        
        
        self.end = self.end + frequency_advance_duration        
