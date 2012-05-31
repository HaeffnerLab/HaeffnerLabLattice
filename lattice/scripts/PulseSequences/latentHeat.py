from sequence import Sequence

class LatentHeat(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                         'initial_cooling':(float, 10e-9, 5.0, 100e-3),
                         'heat_delay':(float, 10e-9, 5.0, 100e-3),
                         'axial_heat':(float, 10e-9, 5.0, 100e-3),
                         'readout_delay':(float, 10e-9, 5.0, 100e-3),
                         'readout_time':(float, 10e-9, 5.0, 100e-3),
                         'xtal_record':(float, 10e-9, 5.0, 100e-3)
                    }
    
    def defineSequence(self):
        initial_cooling = self.vars['initial_cooling']
        heat_delay = self.vars['heat_delay']
        axial_heat = self.vars['axial_heat']
        readout_delay = self.vars['readout_delay']
        readout_time = self.vars['readout_time']
        xtal_record =  self.vars['xtal_record']
        
        globalofftime = heat_delay + axial_heat + readout_delay
        recordTime = initial_cooling + heat_delay + axial_heat + readout_delay + readout_time + xtal_record
        startHeat = initial_cooling + heat_delay
        endHeat = initial_cooling + heat_delay + axial_heat
        startReadout = endHeat + readout_delay
        start_xtal = startReadout + readout_time
        
        self.pulser.add_ttl_pulse('TimeResolvedCount', 0.0, recordTime) #record the whole time
        self.pulser.add_ttl_pulse('110DP', initial_cooling, globalofftime) #turn off blue light during heating
        self.pulser.add_ttl_pulse('110DPlist', initial_cooling, 10e-6) #advance frequency of RS
        self.pulser.add_ttl_pulse('axial', startHeat, axial_heat) #heat with the far blue axial beam
        #make sure there is no cooling by also switching off 866 when there is no 397 light.
        self.pulser.add_ttl_pulse('866DP', initial_cooling, heat_delay )
        self.pulser.add_ttl_pulse('866DP', endHeat, readout_delay )
        self.pulser.add_ttl_pulse('camera', startReadout, 10e-6)
        self.pulser.add_ttl_pulse('110DPlist', start_xtal, 10e-6) #advance frequency of RS at the end of the sequence

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
                         'cooling_ampl_866':(float, -63.0, -3.0, -43.0)
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
        pulser.add_ttl_pulse('110DPlist', p.backgroundMeasure + p.initial_cooling, 10e-6) #advance frequency of RS
        pulser.add_ttl_pulse('axial', startHeat, p.axial_heat) #heat with the far blue axial beam
        #make sure there is no cooling by also switching off 866 when there is no 397 light.
        pulser.add_ttl_pulse('866DP', p.backgroundMeasure + p.initial_cooling, p.heat_delay )
        pulser.add_ttl_pulse('866DP', endHeat, p.readout_delay )
        pulser.add_ttl_pulse('camera', startReadout, 10e-6)
        pulser.add_ttl_pulse('110DPlist', start_xtal, 10e-6) #advance frequency of RS at the end of the sequence
        #adding dds settings for the 866DP
        pulser.add_dds_pulses('866DP', [(40e-9, 80.0 , p.cooling_ampl_866)]) #start by cooling
        pulser.add_dds_pulses('866DP', [(endHeat, 80.0 , p.readout_ampl_866)]) #
        pulser.add_dds_pulses('866DP', [(start_xtal, 80.0 , p.cooling_ampl_866)])
        

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = LatentHeatBackground(pulser)
    pulser.new_sequence()
    params = {
              'initial_cooling': 25e-3,
              'heat_delay':10e-3,
              'axial_heat':18.0*10**-3,
              'readout_delay':1.0*10**-3,
              'readout_time':10.0*10**-3,
              'xtal_record':25e-3
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