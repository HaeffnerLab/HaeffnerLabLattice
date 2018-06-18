from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class MolmerSorensen(pulse_sequence):
    
    
    def sequence(self):
        

        slope_dict = {0:0.0, 1:1.0, 2:2.0, 3: 3.0, 4:4.0, 6:600.0}

        p = self.parameters.MolmerSorensen 
        frequency_advance_duration = WithUnit(6, 'us')
        
        try:
            slope_duration = WithUnit(int(slope_dict[p.shape_profile]),'us')
        except KeyError:
            raise Exception('Cannot find shape profile: ' + str(p.shape_profile))
        
        ampl_off = WithUnit(-63.0, 'dBm')
        

        # # Set frequency of the global
        # self.addDDS('729global', self.start, frequency_advance_duration, p.frequency, ampl_off)

        

        # if p.bichro_enable:# and not p.enable_DD:
        #     slope_duration = WithUnit(4, "us")
        #     self.end = self.start + 2*frequency_advance_duration + p.duration + slope_duration


        #     self.addTTL('bichromatic_1', self.start, p.duration + 2*frequency_advance_duration + slope_duration)
        #     self.addDDS('729global', self.start + frequency_advance_duration, slope_duration, p.frequency, 
        #                 p.amplitude, p.phase, profile=2)
        #     self.addDDS('729global', self.start + frequency_advance_duration + slope_duration, p.duration, 
        #                 p.frequency, p.amplitude, p.phase, profile=4)
        #     # making sure that the local is off -> enabling the turned off sp and detuing the beam
        #     self.addDDS('729local', self.start , p.duration + frequency_advance_duration + slope_duration, 
        #                 WithUnit(220.0, 'MHz'), ampl_off)
                
                
        #     if (p.due_carrier_enable):
        #         self.addDDS('729global_1', self.start, frequency_advance_duration, p.frequency_ion2, ampl_off)
        #         self.addDDS('729global_1', self.start + frequency_advance_duration, slope_duration, p.frequency_ion2, 
        #                     p.amplitude_ion2, p.phase, profile=2)
        #         self.addDDS('729global_1', self.start + frequency_advance_duration + slope_duration, p.duration, 
        #                     p.frequency_ion2, p.amplitude_ion2, p.phase, profile=4)

                    

        #     self.addDDS('729global', self.start + p.duration + frequency_advance_duration + slope_duration, 
        #                 frequency_advance_duration, p.frequency, ampl_off, profile=0)
        #     self.addDDS('729local', self.start + p.duration + frequency_advance_duration + slope_duration, 
        #                 frequency_advance_duration, WithUnit(220.0, "MHz"), ampl_off)        
        #     if (p.due_carrier_enable):
        #         self.addDDS('729global_1', self.start + p.duration + frequency_advance_duration + slope_duration, 
        #                 frequency_advance_duration, p.frequency, ampl_off, profile=0)
                
            


        # Set frequency of the global
        self.addDDS('729global', self.start, frequency_advance_duration, p.frequency, ampl_off)

        if p.bichro_enable:# and not p.enable_DD:
            
            slope_duration = WithUnit(2, "us")
            self.end = self.start + 2*frequency_advance_duration + p.duration + slope_duration

           

            self.addTTL('bichromatic_1', self.start, p.duration + 1*frequency_advance_duration + slope_duration)
            self.addDDS('729global', self.start + frequency_advance_duration, p.duration, p.frequency, 
                        p.amplitude, p.phase, profile=2)
            # making sure that the local is off -> enabling the turned off sp and detuing the beam
            self.addDDS('729local', self.start , p.duration + frequency_advance_duration + slope_duration, 
                        WithUnit(220.0, 'MHz'), ampl_off)
                
                
            if (p.due_carrier_enable):
                self.addDDS('729global_1', self.start, frequency_advance_duration, p.frequency_ion2, ampl_off)
                self.addDDS('729global_1', self.start + frequency_advance_duration, p.duration, p.frequency_ion2, 
                            p.amplitude_ion2, p.phase, profile=2)

                    

            self.addDDS('729global', self.start + p.duration + 1*frequency_advance_duration + slope_duration, 
                        frequency_advance_duration, p.frequency, ampl_off, profile=2)
            self.addDDS('729local', self.start + p.duration + 1*frequency_advance_duration + slope_duration, 
                        frequency_advance_duration, WithUnit(220.0, "MHz"), ampl_off)        
            # if (p.due_carrier_enable):
            #     self.addDDS('729global_1', self.start + p.duration + frequency_advance_duration + slope_duration, 
            #                 frequency_advance_duration, p.frequency_ion2, ampl_off, profile=int(p.shape_profile))
                
                #self.end = self.end + frequency_advance_duration

            

        # elif p.bichro_enable and p.enable_DD:
            



            # N = int(p.num_DD_pulses)
            
            # # Set the amplitude for local to lowest value during sequence
            # self.addDDS('729local', self.start , p.duration + 2*N*frequency_advance_duration + N*p.analysis_duration*2, 
            #             WithUnit(220.0, 'MHz'), ampl_off)

            # # Advance frequency global_2
            # self.addDDS('729global_2', self.start, frequency_advance_duration, p.frequency, ampl_off)

            # # Use analysis amplitudes for global pi-pulses
            # analysis_amp_ion1 = p.analysis_amplitude
            # analysis_amp_ion2 = p.analysis_amplitude_ion2

            
            # # This is the sequence's time tracker
            # current_time = self.start + frequency_advance_duration

            # for i in range(N):
            #     if i == 0:
            #         # Shape the first bichro pulse, not sure if this helps or hurts
            #         profile = 0#profile = int(p.shape_profile)
            #     else:
            #         profile = 0

            #     # Turn bichro switch on just long enough to run a single bichro pulse
            #     self.addTTL('bichromatic_1', current_time, p.duration/(N+1) + frequency_advance_duration)
            #     print("Current bichro time", current_time)

            #     # Add bichro pulse
            #     self.addDDS("729global", current_time, p.duration/(N+1), p.frequency, 
            #                 p.amplitude, profile=profile)

            #     current_time += p.duration/(N+1)

            #     # And turn it off
            #     self.addDDS("729global", current_time, frequency_advance_duration, p.frequency, ampl_off, profile=profile)

            #     current_time += frequency_advance_duration + WithUnit(2, "us")

            #     # Add single-tone pi-rotation, flip phase of every other rotation
            #     self.addDDS("729global_2", current_time, p.analysis_duration*2, p.frequency, analysis_amp_ion1,
            #                 WithUnit(180, "deg")) #  WithUnit(180 * (i%2), "deg"))

            #     current_time += p.analysis_duration*2

            #     # And turn it off
            #     self.addDDS("729global_2", current_time, frequency_advance_duration, p.frequency, ampl_off)#WithUnit(180, "deg")) #  WithUnit(180 * (i%2), "deg"))
    
            #     current_time += frequency_advance_duration + WithUnit(2, "us")
            
            
            # # Run final bichro pulse
            # self.addTTL('bichromatic_1', current_time, p.duration/(N+1) + frequency_advance_duration)
            # print("Current bichro time", current_time)
            # self.addDDS('729global', current_time, p.duration/(N+1), p.frequency, p.amplitude)

            
            # current_time += p.duration/(N+1)

            # # Here we ramp off lasers, not sure if this helps or hurts in DD sequence
            # self.addDDS('729global', current_time, frequency_advance_duration, p.frequency, ampl_off, profile=0)


            # # Finally turn off local and advance global pulse sequence time
            # self.addDDS('729local', current_time, frequency_advance_duration, p.frequency, ampl_off)
            # self.end = current_time + 2 * frequency_advance_duration

        else: # bichro not enabled

            if p.use_analysis_amplitudes:
                amp_ion1 = p.analysis_amplitude
                amp_ion2 = p.analysis_amplitude_ion2
            else:
                amp_ion1 = p.amplitude
                amp_ion2 = p.amplitude_ion2

            self.end = self.start + frequency_advance_duration + p.duration

            self.addDDS('729global', self.start + frequency_advance_duration, p.duration, p.frequency, 
                        amp_ion1, p.phase)
            # making sure that the local is off -> enabling the turned off sp and detuing the beam
            self.addDDS('729local', self.start , p.duration + frequency_advance_duration, 
                        WithUnit(220.0, 'MHz'), ampl_off)

            if p.due_carrier_enable:
                self.addDDS('729global_1', self.start, frequency_advance_duration, p.frequency_ion2, ampl_off)
                self.addDDS('729global_1', self.start + frequency_advance_duration, p.duration, p.frequency_ion2, 
                            amp_ion2, p.phase)

                #self.addTTL('bichromatic_1', self.start, p.duration + frequency_advance_duration)

            self.addDDS('729global', self.start + p.duration + frequency_advance_duration, 
                        frequency_advance_duration, p.frequency, ampl_off)
            self.addDDS('729local', self.start + p.duration + frequency_advance_duration, 
                        frequency_advance_duration, p.frequency, ampl_off)

            if p.due_carrier_enable:
                self.addDDS('729global_1', self.start + p.duration + frequency_advance_duration, 
                            frequency_advance_duration, p.frequency_ion2, ampl_off)