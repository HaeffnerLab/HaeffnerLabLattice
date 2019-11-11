from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class VAET(pulse_sequence):
    
        
    def sequence(self):
        
        ms = self.parameters.MolmerSorensen
        v = self.parameters.VAET
        szx = self.parameters.SZX
        duration = v.vaet_duration

        frequency_advance_duration = U(6., "us")
        ampl_off = U(-63, "dBm")
        shape_profile = 0
        slope_duration = U(0, "us")

        self.end = self.start + 3 * frequency_advance_duration + duration + slope_duration
        
        #first advance the frequency but keep amplitude low
        self.addDDS("729global", self.start, frequency_advance_duration, ms.frequency, ampl_off)
        self.addDDS("729local", self.start, frequency_advance_duration, szx.frequency, ampl_off)
        if ms.due_carrier_enable:
            self.addDDS("729global_1", self.start, frequency_advance_duration, ms.frequency_ion2, ampl_off)

        self.addDDS("729global", self.start + frequency_advance_duration, duration, ms.frequency, 
                    ms.amplitude, ms.phase, profile=shape_profile)
        self.addDDS("729local", self.start + frequency_advance_duration, duration, szx.frequency,
                    szx.amplitude, szx.phase, profile=shape_profile)
        if ms.due_carrier_enable:
            self.addDDS("729global_1", self.start, frequency_advance_duration, ms.frequency_ion2, ms.amplitude_ion2,
                        ms.phase, profile=shape_profile)

        if ms.bichro_enable:
            self.addTTL("bichromatic_1", self.start, duration + 2 * frequency_advance_duration + slope_duration)
        if szx.bichro_enable:
            #pass
            self.addTTL("bichromatic_2", self.start, duration + 2 * frequency_advance_duration + slope_duration)

        # Turning of DP gradually
        self.addDDS("729global", self.start + duration + 2 * frequency_advance_duration + slope_duration, 
                    frequency_advance_duration, ms.frequency, ampl_off)
        self.addDDS("729local", self.start + duration + 2 * frequency_advance_duration + slope_duration, 
                    frequency_advance_duration, szx.frequency, ampl_off)
        if ms.due_carrier_enable:
            self.addDDS("729global_1", self.start + duration + 2 * frequency_advance_duration + slope_duration,
                    frequency_advance_duration, ms.frequency_ion2, ampl_off)        
