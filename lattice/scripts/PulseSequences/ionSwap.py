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
        cameraPulse = 10e-6
        
        #p.backgroundMeasure = p.exposure #measure background for the same time as camera exposure
        
        #globalofftime = p.heat_delay + p.axial_heat + p.readout_delay
        # recordTime will add some more stuff
        #p.recordTime = p.backgroundMeasure + p.initial_cooling + globalofftime + p.readout_time + p.xtal_record
        
        #startHeat = p.backgroundMeasure + p.initial_cooling + p.heat_delay
        #endHeat = startHeat + p.axial_heat
        #startReadout = endHeat + p.readout_delay
        #start_xtal = startReadout + p.readout_time
        
#        startBackground = 0.0
#        endBackground = p.exposure
#        backgroundDuration = endBackground - startBackground

        # measure background for the same time as camera exposure        
        startFirstExposure = 0.0
        endFirstExposure = p.exposure + cameraPulse
        firstExposureDuration = endFirstExposure - startFirstExposure
        
        startSecondExposure = endFirstExposure + p.camera_delay + p.initial_cooling
        endSecondExposure = startSecondExposure + p.exposure + cameraPulse
#        secondExposureDuration = endSecondExposure - startSecondExposure
        
        startDarkening = endSecondExposure + p.camera_delay
        endDarkening = startDarkening + p.darkening
        darkeningDuration = endDarkening - startDarkening
        
        startThirdExposure = endDarkening
        endThirdExposure = endDarkening + p.exposure + cameraPulse
#        thirdExposureDuration = endSecondExposure - startSecondExposure
         
        startGlobalOff = endThirdExposure + p.camera_delay
        endGlobalOff = startGlobalOff + p.heat_delay + p.axial_heat + p.readout_delay
        globalOffDuration = endGlobalOff - startGlobalOff
        
        startHeat = startGlobalOff + p.heat_delay
        endHeat = startHeat + p.axial_heat
        heatDuration = endHeat - startHeat
        
        p.startReadout = endHeat + p.readout_delay
        p.stopReadout = p.startReadout + p.readout_time
        
        startFourthExposure = endHeat + p.readout_delay + p.readout_time + p.rextal_time
        endFourthExposure = startFourthExposure + p.exposure + cameraPulse
#        fourthExposureDuration = endFourthExposure - startFourthExposure

        startBrightening = endFourthExposure + p.camera_delay
        endBrightening = startBrightening + p.brightening
        brighteningDuration = endBrightening - startBrightening
        
        p.recordTime =  startBrightening + brighteningDuration - startFirstExposure
              
#        pulser.add_ttl_pulse('TimeResolvedCount', startFirstExposure, p.recordTime) #record the whole time
        #measure the background first: switch off 866 and keep 110DP on
#        pulser.add_ttl_pulse('866DP', startFirstExposure, firstExposureDuration)
#        pulser.add_ttl_pulse('camera', startFirstExposure, cameraPulse)        
        # wait through the camera delay and initial cooling  before taking the 'initial' picture
        pulser.add_dds_pulses('866DP', [(40e-9, 80.0 , p.cooling_ampl_866)]) #start by cooling
        pulser.add_ttl_pulse('camera', startSecondExposure, cameraPulse)        
        # wait through the camera delay and shine the 729
        pulser.add_ttl_pulse('729DP', startDarkening, darkeningDuration)
        # take a picture of the dark ions
        pulser.add_ttl_pulse('camera', endDarkening, cameraPulse)
        # when DDS works, comment out!
        # DDS should happen right before readout (but enough time before so that it switches completely
        # , and after readout (during recrystalization
#        pulser.add_ttl_pulse('110DPlist', p.backgroundMeasure + p.initial_cooling, 10e-6) #advance frequency of RS
        
        # stop cooling during heating
        pulser.add_ttl_pulse('110DP', startGlobalOff, globalOffDuration)
        #make sure there is no cooling by also switching off 866 when there is no 397 light.
        pulser.add_ttl_pulse('866DP', startGlobalOff, p.heat_delay )
        pulser.add_ttl_pulse('axial', startHeat, heatDuration) #heat with the far blue axial beam
        pulser.add_dds_pulses('866DP', [(endHeat, 80.0 , p.readout_ampl_866)]) #
        pulser.add_ttl_pulse('866DP', endHeat, p.readout_delay)
        # another DDS move (amplitude increased)
#        pulser.add_ttl_pulse('110DPlist..
        # take the last picture
        pulser.add_ttl_pulse('camera', startFourthExposure, cameraPulse)
        # make all the ions bright again
        pulser.add_ttl_pulse('854DP', startBrightening, brighteningDuration)
        
        #adding dds settings for the 866DP
        pulser.add_dds_pulses('866DP', [(start_xtal, 80.0 , p.xtal_ampl_866)])
        #adding dds settings for the 110DP
        pulser.add_dds_pulses('110DP', [(40e-9, p.cooling_freq_397 , p.cooling_ampl_397)]) #start by cooling
        pulser.add_dds_pulses('110DP', [(endHeat, p.readout_freq_397 , p.readout_ampl_397)]) #readout
        pulser.add_dds_pulses('110DP', [(start_xtal, p.xtal_freq_397 , p.xtal_ampl_397)]) #xtal
        

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