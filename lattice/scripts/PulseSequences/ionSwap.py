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
                         'brightening': (float, 10e-9, 1.0, 10e-3)
                    }
    
    def defineSequence(self):   
        p = self.parameters
        pulser = self.pulser
        
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
        endFirstExposure = p.exposure
        firstExposureDuration = endFirstExposure - startFirstExposure
        
        startSecondExposure = endFirstExposure + p.camera_delay + p.initial_cooling
        endSecondExposure = startSecondExposure + p.exposure 
        secondExposureDuration = endSecondExposure - startSecondExposure
        
        startDarkening = endSecondExposure + p.camera_delay
        endDarkening = startDarkening + p.darkening
        darkeningDuration = endDarkening - startDarkening
        
        startThirdExposure = endDarkening
        endThirdExposure = endDarkening + p.exposure
        thirdExposureDuration = endSecondExposure - startSecondExposure
         
        startGlobalOff = endThirdExposure + p.camera_delay
        endGlobalOff = startGlobalOff + p.heat_delay + p.axial_heat + p.readout_delay
        globalOffDuration = endGlobalOff - startGlobalOff
        
        startHeat = startGlobalOff + p.heat_delay
        endHeat = startHeat + p.axial_heat
        heatDuration = endHeat - startHeat
        
        startFourthExposure = endHeat + p.heat_delay + p.readout_time + p.rextal_time
        endFourthExposure = startFourthExposure + p.exposure
        fourthExposureDuration = endFourthExposure - startFourthExposure

        startBrightening = endFourthExposure + p.camera_delay
        endBrightening = startBrightening + p.brightening
        brighteningDuration = endBrightening - startBrightening
        
        pulser.add_ttl_pulse('TimeResolvedCount', startBackground, p.recordTime) #record the whole time
        #measure the background first: switch off 866 and keep 110DP on
        pulser.add_ttl_pulse('866DP', startFirstExposure, firstExposureDuration)
        pulser.add_ttl_pulse('camera', startFirstExposure, firstExposureDuration)        
        # wait through the camera delay and initial cooling  before taking the 'initial' picture
        pulser.add_ttl_pulse('camera', startSecondExposure, secondExposureDuration)        
        # wait through the camera delay and shine the 729
        pulser.add_ttl_pulse('729DP', startDarkening, darkeningDuration)
        # take a picture of the dark ions
        pulser.add_ttl_pulse('camera', endDarkening, thirdExposureDuration)
        # when DDS works, comment out!
        # DDS should happen right before readout (but enough time before so that it switches completely
        # , and after readout (during recrystalization
#        pulser.add_ttl_pulse('110DPlist', p.backgroundMeasure + p.initial_cooling, 10e-6) #advance frequency of RS
        
        # stop cooling during heating
        pulser.add_ttl_pulse('110DP', startGlobalOff, globalOffDuration)
        #make sure there is no cooling by also switching off 866 when there is no 397 light.
        pulser.add_ttl_pulse('866DP', startGlobalOff, p.heat_delay )
        pulser.add_ttl_pulse('axial', startHeat, heatDuration) #heat with the far blue axial beam
        pulser.add_ttl_pulse('866DP', endHeat, p.readout_delay)
        # another DDS move (amplitude increased)
#        pulser.add_ttl_pulse('110DPlist..
        # take the last picture
        pulser.add_ttl_pulse('camera', startFourthExposure, fourthExposureDuration)
        # make all the ions bright again
        pulser.add_ttl_pulse('854DP', startBrightening, brighteningDuration)

if __name__ == '__main__':
    import labrad
    import plotsequence
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = IonSwapBackground(pulser)
    pulser.new_sequence()
    params = { 
              'exposure': .1,
              'camera_delay': .02, 
              'initial_cooling': 1.,
              'darkening': .1,
              'heat_delay':1.,
              'axial_heat':1.,
              'readout_delay':1.,
              'readout_time':1.,
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