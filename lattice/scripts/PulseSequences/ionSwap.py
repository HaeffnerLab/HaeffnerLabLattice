from sequence import Sequence


class IonSwapBackground(Sequence):
    """Ion Swap pulse sequence that also includes a period of heating beam on, 866 off to measure the background from that beam"""
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                         'exposure': (float, 30e-3, 1.0, 100e-3),
                         'camera_delay': (float, 10e-9, 1.0, 10e-3),
                         'darkening': (float, 10e-9, 1.0, 10e-3),
                         'initial_cooling':(float, 10e-9, 5.0, 100e-3),
                         'heat_delay':(float, 10e-9, 5.0, 100e-3),
                         'axial_heat':(float, 10e-9, 5.0, 100e-3),
                         'readout_delay':(float, 10e-9, 5.0, 100e-3),
                         'readout_time':(float, 10e-9, 5.0, 100e-3),
                         'rextal_time': (float, 10e-9, 5.0, 50e-3),
                         'brightening': (float, 10e-9, 1.0, 10e-3),
                         'readout_ampl_866':(float, -63.0, -3.0, -63.0),
                         'heating_ampl_866':(float, -63.0, -3.0, -63.0),
                         'cooling_ampl_866':(float, -63.0, -3.0, -63.0),
                         'xtal_ampl_866':(float, -63.0, -3.0, -63.0),
                         'cooling_freq_397':(float, 90.0,130.0, 110.0),
                         'cooling_ampl_397':(float,-63.0, -3.0, -63.0),
                         'readout_freq_397':(float, 90.0,130.0, 110.0),
                         'readout_ampl_397':(float,-63.0, -3.0, -63.0),
                         'xtal_freq_397':(float, 90.0,130.0, 110.0),
                         'xtal_ampl_397':(float,-63.0, -3.0, -63.0),
                         'repumpPower':(float, -63.0, -3.0, -3.0)
                         
                    }
    
    def defineSequence(self):   
        p = self.parameters
        pulser = self.pulser
        cameraPulse = 10e-6
               
        startFirstExposure = p.initial_cooling
        endFirstExposure = startFirstExposure + p.exposure + cameraPulse
        
        startDarkening = endFirstExposure + p.camera_delay        
        endDarkening = startDarkening + p.darkening        
        darkeningDuration = endDarkening - startDarkening
        
        startSecondExposure = endDarkening        
        endSecondExposure = endDarkening + p.exposure + cameraPulse
         
        startGlobalOff = endSecondExposure + p.camera_delay
        endGlobalOff = startGlobalOff + p.heat_delay + p.axial_heat + p.readout_delay
        globalOffDuration = endGlobalOff - startGlobalOff
        
        startHeat = startGlobalOff + p.heat_delay
        endHeat = startHeat + p.axial_heat
        heatDuration = endHeat - startHeat
        
        p.startReadout = endHeat + p.readout_delay
        p.endReadout = p.startReadout + p.readout_time
              
        start_rextal = endHeat + p.readout_delay + p.readout_time

        startThirdExposure = start_rextal + p.rextal_time
        endThirdExposure = startThirdExposure + p.exposure + cameraPulse
        
        startBrightening = endThirdExposure + p.camera_delay
        endBrightening = startBrightening + p.brightening
        brighteningDuration = endBrightening - startBrightening
        
        p.recordTime =  startBrightening + brighteningDuration
              
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0, p.recordTime) #record the whole time
        # make all the ions bright again
        pulser.add_dds_pulses('110DP', [(40e-9, p.cooling_freq_397 , p.cooling_ampl_397)]) #start by cooling
        # wait through the initial cooling before taking the 'initial' picture
        pulser.add_dds_pulses('866DP', [(40e-9, 80.0 , p.cooling_ampl_866)]) #start by cooling
        pulser.add_ttl_pulse('camera', startFirstExposure, cameraPulse)        
        # wait through the camera delay and shine the 729
        pulser.add_ttl_pulse('729DP', startDarkening, darkeningDuration)
        # take a picture of the dark ions
        pulser.add_ttl_pulse('camera', startSecondExposure, cameraPulse)  
        # stop cooling during heating
        pulser.add_ttl_pulse('110DP', startGlobalOff, globalOffDuration)
        # make sure there is no cooling by also switching off 866 when there is no global 397 light.
        pulser.add_ttl_pulse('866DP', startGlobalOff, p.heat_delay )
        pulser.add_ttl_pulse('axial', startHeat, heatDuration) #heat with the far blue axial beam
        pulser.add_dds_pulses('866DP', [(endHeat, 80.0 , p.readout_ampl_866)]) #
        # again, make sure there is no cooling right before readout
        pulser.add_ttl_pulse('866DP', endHeat, p.readout_delay)
        pulser.add_dds_pulses('110DP', [(endHeat, p.readout_freq_397 , p.readout_ampl_397)]) #readout
        # after readout, adjust amplitudes for recrystalization
        pulser.add_dds_pulses('866DP', [(start_rextal, 80.0 , p.xtal_ampl_866)])
        pulser.add_dds_pulses('110DP', [(start_rextal, p.xtal_freq_397 , p.xtal_ampl_397)]) #xtal

        # take the last picture
        pulser.add_ttl_pulse('camera', startThirdExposure, cameraPulse)
        
        pulser.add_dds_pulses('854DP', [(startBrightening, 80.0, p.repumpPower)])
        pulser.add_dds_pulses('854DP', [(endBrightening, 80.0, -63.0)])

        

if __name__ == '__main__':
    import labrad
    from plotsequence import SequencePlotter
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = IonSwapBackground(pulser)
    pulser.new_sequence()
    params = { 
              'exposure': .1,
              'camera_delay': .02, 
              'initial_cooling': .115, #includes delay 15ms delay after background collection
              'darkening': .1,
              'heat_delay':.005,
              'axial_heat':.02,
              'readout_delay':.005,
              'readout_time':.01,
              'rextal_time': .05,
              'brightening': .01,
              }
    seq.setVariables(**params)
    seq.defineSequence()
#    pulser.program_sequence()
#    pulser.reset_timetags()
#    pulser.start_single()
#    pulser.wait_sequence_done()
#    pulser.stop_sequence()
#    timetags = pulser.get_timetags().asarray
#    print timetags
    
    hr = pulser.human_readable().asarray
    channels = pulser.get_channels().asarray
    sp = SequencePlotter(hr, channels)
    sp.makePlot()