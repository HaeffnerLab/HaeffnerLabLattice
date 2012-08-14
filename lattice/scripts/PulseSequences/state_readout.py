from sequence import Sequence

class state_readout(Sequence):
        
    requiredVars = {
                    'frequencies_729':(float, 150.0, 250.0, 220.0),
                    'amplitudes_729':(float, -63.0, -3.0,   -3.0),
                    'doppler_cooling':(float, 10e-9, 100*10**-3, 1.0*10**-3),
                    'doppler_cooling_freq':(float, 90.0, 130.0, 110.0),
                    'doppler_cooling_ampl':(float, -63.0, -3.0,   -11.0),
                    'readout_freq':(float, 90.0, 130.0, 110.0),
                    'readout_ampl':(float, -63.0, -3.0,   -11.0),
                    'rabi_time':(float, 10e-9, 1000*10**-3, 1.0*10**-3),
                    'readout_time':(float, 10e-9, 100*10**-3, 1.0*10**-3),
                    'repump_time':(float, 10e-9, 100*10**-3, 1.0*10**-3),
                    'repump_854_ampl': (float, -63.0, -3.0,   -11.0),
                    'repump_866_ampl': (float, -63.0, -3.0,   -11.0),
                    'optical_pump_freq':(float, 150.0, 250.0, 220.0),
                    'optical_pump_ampl': (float, -63.0, -3.0,   -6.0),
                    'optical_pump_dur':(float, 10e-9, 100*10**-3, 1.0*10**-3),
                    'optical_pump_ratio':(float, 0.1, 1.0, 1.0),
                    'repump_freq_854':(float, 70.0, 90.0, 80.0),
                    'repump_freq_866':(float, 70.0, 90.0, 80.0),
                    }
    
    def defineSequence(self):  
        
        p = self.parameters
        pulser = self.pulser
        offset = 100e-6 
        #computing the times
        p.cycleTime = p.repump_time + p.doppler_cooling + p.heating_time + p.rabi_time + p.readout_time + p.optical_pump_dur
        cT = p.cycleTime
        start_cooling = offset
        repump_854_off = offset + p.repump_time
        cooling_off = repump_854_off + p.doppler_cooling
        start_optical_pump = cooling_off
        rabi_on = cooling_off + p.heating_time + p.optical_pump_dur
        rabi_off = rabi_on + p.rabi_time
        readout_on = rabi_off
        freqs = p.frequencies_729
        ampls = p.amplitudes_729
        #lists for programming
        coolingOn = []
        coolingOff = []
        repump854On = []
        repump854Off = []
        repump866On = []
        repump866Off = []
        rabiOn = []
        rabiOff = []
        readoutOn = []
        readoutOff = []
        readout_count = []
        for i in range(len(freqs)):
            rabiOff.append(      (offset + i  * cT, 0.0, -63.0) )      
            coolingOn.append(    (start_cooling + i  * cT, p.doppler_cooling_freq, p.doppler_cooling_ampl)  )
            repump866On.append(  (start_cooling + i  * cT, p.repump_freq_866, p.repump_866_ampl)  )
            #optical pummping
            rabiOn.append(       (start_optical_pump + i  * cT, p.optical_pump_freq, p.optical_pump_ampl) )
            rabiOff.append(      (start_optical_pump + p.optical_pump_dur/2.0 + i  * cT, 0.0, -63.0) )
            repump854On.append(  (start_optical_pump + i  * cT, p.repump_freq_854, p.repump_854_ampl)  )
            repump854Off.append( (start_optical_pump + p.optical_pump_dur + i  * cT, p.repump_freq_866, -63.0)  )
            #rest
            repump854On.append(  (start_cooling + i  * cT, p.repump_freq_854, p.repump_854_ampl)  )
            repump854Off.append( (repump_854_off + i  * cT, p.repump_freq_854, -63.0)  )
            coolingOff.append(   (cooling_off + i  * cT, p.doppler_cooling_freq, -63.0)  )
            repump866Off.append( (cooling_off + i  * cT, p.repump_freq_866, -63.0)  )
            rabiOn.append(       (rabi_on + i  * cT, freqs[i], ampls[i]) )
            rabiOff.append(      (rabi_off + i  * cT, 0.0, -63.0) )
            readoutOn.append(    (readout_on + i  * cT, p.readout_freq, p.readout_ampl  ))
            repump866On.append(  (readout_on + i  * cT, p.repump_freq_866, p.repump_866_ampl)  )
            readout_count.append( ('ReadoutCount', readout_on + i  * cT, p.readout_time)) 
        pulser.add_ttl_pulses(readout_count)
        for channel, pulses in [
                                ('110DP', coolingOn), ('110DP', coolingOff), ('110DP', readoutOn), ('110DP', readoutOff),
                                ('854DP', repump854On), ('854DP', repump854Off),
                                ('866DP', repump866On), ('866DP', repump866Off),
                                ('729DP', rabiOn),('729DP', rabiOff),
                                ]:
            pulser.add_dds_pulses(channel, pulses)
        
if __name__ == '__main__':
    import labrad
    import numpy
    freqs = numpy.arange(210.0, 220.0, 0.5)
    ampls = numpy.ones_like(freqs) * -11.0
    freqs = freqs.tolist()
    ampls = ampls.tolist()
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = state_readout(pulser)
    pulser.new_sequence()
    params = {
                'frequencies_729':freqs,
                'amplitudes_729': ampls,
                'doppler_cooling':100*10**-3,
                'heating_time':100e-9,
                'rabi_time':5*10**-3,
                'readout_time':50*10**-3,
                'repump_time':5*10**-3,
                'repump_854_ampl': -3.0,
                'repump_866_ampl': -11.0,
                'doppler_cooling_freq':103.0,
                'doppler_cooling_ampl':-11.0,
                'readout_freq':103.0,
                'readout_ampl':-11.0
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.reset_timetags()
    pulser.start_number(1)
    #pulser.start_single()
    #pulser.start_looped()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    readouts = pulser.get_readout_counts().asarray
    print readouts.size
    print readouts
    