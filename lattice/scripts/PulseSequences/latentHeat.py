from sequence import Sequence

class LatentHeatBackground(Sequence):
    """Same as Latent Heat pulse sequence but also includes a period of heating beam on, 866 off to measure the background from that beam"""
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                         'initial_cooling':(float, 10e-9, 5.0, 100e-3),
                         'heat_delay':(float, 10e-9, 5.0, 100e-3),
                         'axial_heat':(float, 10e-9, 5.0, 100e-3),
                         'readout_delay':(float, 10e-9, 5.0, 100e-3),
                         'readout_time':(float, 10e-9, 5.0, 100e-3),
                         'xtal_record':(float, 10e-9, 5.0, 100e-3),
                         'readout_ampl_866':(float, -63.0, -3.0, -63.0),
                         'cooling_ampl_866':(float, -63.0, -3.0, -63.0),
                         'xtal_ampl_866':(float, -63.0, -3.0, -63.0),
                         'cooling_freq_397':(float, 90.0,130.0, 110.0),
                         'cooling_ampl_397':(float,-63.0, -3.0, -63.0),
                         'readout_freq_397':(float, 90.0,130.0, 110.0),
                         'readout_ampl_397':(float,-63.0, -3.0, -63.0),
                         'xtal_freq_397':(float, 90.0,130.0, 110.0),
                         'xtal_ampl_397':(float,-63.0, -3.0, -63.0)
    }
    
    def defineSequence(self):   
        p = self.parameters
        pulser = self.pulser
        
        p.backgroundMeasure = p.axial_heat #measure background for the same time as the heating
        
        globalofftime = p.heat_delay + p.axial_heat + p.readout_delay
        p.recordTime = p.backgroundMeasure + p.initial_cooling + globalofftime + p.readout_time + p.xtal_record
        startHeat = p.backgroundMeasure + p.initial_cooling + p.heat_delay
        endHeat = startHeat + p.axial_heat
        startReadout = endHeat + p.readout_delay
        start_xtal = startReadout + p.readout_time
        
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0, p.recordTime) #record the whole time
        #measure the background first: turn on axial beam, switch off 866 and 110DP
        pulser.add_ttl_pulse('axial',0.0, p.backgroundMeasure)
        pulser.add_ttl_pulse('866DP', 0.0, p.backgroundMeasure)
        pulser.add_ttl_pulse('110DP', 0.0, p.backgroundMeasure)
        #let it cool until time to switch off the global again
        pulser.add_ttl_pulse('110DP', p.backgroundMeasure + p.initial_cooling, globalofftime) #turn off blue light during heating
        pulser.add_ttl_pulse('axial', startHeat, p.axial_heat) #heat with the far blue axial beam
        #make sure there is no cooling by also switching off 866 when there is no 397 light.
        pulser.add_ttl_pulse('866DP', p.backgroundMeasure + p.initial_cooling, p.heat_delay )
        pulser.add_ttl_pulse('866DP', endHeat, p.readout_delay )
        #adding dds settings for the 866DP
        pulser.add_dds_pulses('866DP', [(40e-9, 80.0 , p.cooling_ampl_866)]) #start by cooling
        pulser.add_dds_pulses('866DP', [(endHeat, 80.0 , p.readout_ampl_866)]) #
        pulser.add_dds_pulses('866DP', [(start_xtal, 80.0 , p.xtal_ampl_866)])
        #adding dds settings for the 110DP
        pulser.add_dds_pulses('110DP', [(40e-9, p.cooling_freq_397 , p.cooling_ampl_397)]) #start by cooling
        pulser.add_dds_pulses('110DP', [(endHeat, p.readout_freq_397 , p.readout_ampl_397)]) #readout
        pulser.add_dds_pulses('110DP', [(start_xtal, p.xtal_freq_397 , p.xtal_ampl_397)]) #xtal
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = LatentHeatBackground(pulser)
    pulser.new_sequence()
    xtalFreq397 = 103.0
    xtalPower397 = -4.0 
    xtalPower866 = -4.0
    #sequence parameters
    params = {
              'initial_cooling': 25e-3,
              'heat_delay':10e-3,
              'axial_heat':18.0*10**-3,
              'readout_delay':1.0*10**-3,
              'readout_time':10.0*10**-3,
              'xtal_record':25e-3,
              'cooling_ampl_866':-3.0,
              'readout_ampl_866':-10.0,
              'xtal_ampl_866':xtalPower866,
              'cooling_freq_397':103.0,
              'cooling_ampl_397':-8.0,
              'readout_freq_397':115.0,
              'readout_ampl_397':-8.0,
              'xtal_freq_397':xtalFreq397,
              'xtal_ampl_397':xtalPower397,
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print 'got {} timetags'.format(timetags.size)