from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class MolmerSorensen(pulse_sequence):
    
    
    def sequence(self):
        
        #this hack will be not needed with the new dds parsing methods
        slope_dict = {0:0.0, 2:2.0, 4:5.0, 6:600.0}
        
        p = self.parameters.MolmerSorensen
        
        pl = self.parameters.LocalStarkShift
        frequency_advance_duration = WithUnit(6, 'us')
        
        
        
        print "212121"
        print "Running MS subseq freq 729: ", p.frequency 
        print "MS params" , self.parameters.MolmerSorensen.ac_stark_shift
        
        
        try:
            slope_duration = WithUnit(int(slope_dict[p.shape_profile]),'us')
        except KeyError:
            raise Exception('Cannot find shape profile: ' + str(p.shape_profile))
        
        ampl_off = WithUnit(-63.0, 'dBm')
        self.end = self.start + 2*frequency_advance_duration + p.duration + slope_duration
        
        #first advance the frequency but keep amplitude low
        self.addDDS('729global', self.start, frequency_advance_duration, p.frequency, ampl_off)
        self.addDDS('729global', self.start + frequency_advance_duration, p.duration, p.frequency, p.amplitude, p.phase, profile=int(p.shape_profile))
#         making sure that the local is off -> enabling the turned off sp and detuing the beam
        self.addDDS('729local', self.start , p.duration+ frequency_advance_duration, WithUnit(220.0, 'MHz'), ampl_off)
        self.addTTL('bichromatic_2', self.start, p.duration + 2*frequency_advance_duration + slope_duration)
        
        if (p.due_carrier_enable):
            print "running due freq"
            print p.amplitude_ion2
            print p.frequency_ion2
            self.addDDS('729global_1', self.start, frequency_advance_duration, p.frequency_ion2, ampl_off)
            self.addDDS('729global_1', self.start + frequency_advance_duration, p.duration, p.frequency_ion2, p.amplitude_ion2, p.phase, profile=int(p.shape_profile))
            
        
        if (p.bichro_enable):
            print "bichro enabled-> running ms gate ioi"
            self.addTTL('bichromatic_1', self.start, p.duration + 2*frequency_advance_duration + slope_duration)
        else:
            print "MS subseq bichro IS NOT enabled-> running a carrier"
#  old pulser had an additional channel for local beam to compensate for B filed gradient         
#         if pl.enable: # add a stark shift on the localized beam
#             f = WithUnit(80. - 0.2, 'MHz') + pl.detuning
#             amp = WithUnit(-10., 'dBm')
#             print p.frequency
#             self.addDDS('SP_local', self.start, frequency_advance_duration, f, ampl_off)
#             self.addDDS('SP_local', self.start + frequency_advance_duration, p.duration, f, pl.amplitude, profile=int(p.shape_profile))
#             
#             # turn on the double pass at -15 dBm for the stark shift
#             self.addDDS('729local', self.start, frequency_advance_duration, p.frequency, ampl_off)
#             self.addDDS('729local', self.start + frequency_advance_duration, p.duration, p.frequency, amp, p.phase, profile=int(p.shape_profile))
#
        # tunning DP off gradually             
        self.addDDS('729global', self.start + p.duration + 2*frequency_advance_duration + slope_duration, frequency_advance_duration, p.frequency, ampl_off)
        self.addDDS('729local', self.start + p.duration + 2*frequency_advance_duration + slope_duration, frequency_advance_duration, p.frequency, ampl_off)        
        if (p.due_carrier_enable):
            self.addDDS('729global_1', self.start + p.duration + 2*frequency_advance_duration + slope_duration, frequency_advance_duration, p.frequency_ion2, ampl_off)
        self.end = self.end + frequency_advance_duration
        
        