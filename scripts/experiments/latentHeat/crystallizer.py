import time
from labrad import types as T
class Crystallizer():
    
    thresholdPercentage = 0.9
    crystallization_attempts = 10
    detect_time = 0.225
    pmtresolution = 0.075
    far_red_time = 0.300
    optimal_cool_time = 0.150
    shutter_delay = 0.025
    rf_crystal_power = -7.0
    rf_settling_time = 0.3
    
    def __init__(self, pulser, pmt, rf):
        self.pulser = pulser
        self.pmt = pmt
        self.rf = rf
        self.crystal_threshold = None

    def get_initial_rate(self):
        self.pmt.set_time_length(self.pmtresolution)
        countNum = int(self.detect_time / self.pmtresolution)
        countRate = self.pmt.get_next_counts('ON', countNum , True)
        self.crystal_threshold = self.thresholdPercentage * countRate
        print 'Crystallizer: Initial Count Rate {0:.2f}, threshold {1:.2f}'.format(countRate, self.crystal_threshold) 
        
    def is_crystallized(self):
        countNum = int(self.detect_time / self.pmtresolution)
        countRate = self.pmt.get_next_counts('ON', countNum , True)
        print 'Crystallizer: Count rate {0:.2f} and threshold is {1:.2f}'.format(countRate, self.crystal_threshold)
        return (countRate > self.crystal_threshold) 
    
    def auto_crystallize(self):       
        if self.is_crystallized():
            print 'Initially Crystallized'
            return True
        else:
            print 'Melted'
            self.pulser.switch_manual('crystallization',  True)
            initpower = self.rf.amplitude()
            for attempt in range(self.crystallization_attempts):
                print 'Crystallizer: attempt number {}'.format(attempt + 1)
                self.rf.amplitude(T.Value(self.rf_crystal_power,'dBm'))
                time.sleep(self.rf_settling_time)
                time.sleep(self.shutter_delay)
                self.pulser.switch_manual('110DP',  False) #turn off DP to get all light into far red 0th order
                time.sleep(self.far_red_time)
                self.pulser.switch_manual('110DP',  True) 
                time.sleep(self.optimal_cool_time)
                self.rf.amplitude(initpower)
                time.sleep(self.rf_settling_time)
                if self.is_crystallized():
                    print 'Crystallized on attempt number {}'.format(attempt + 1)                    
                    self.pulser.switch_manual('crystallization',  False)
                    time.sleep(self.shutter_delay)
                    self.pulser.switch_auto('110DP',  False)
                    return True
            #if still not crystallized, let the user handle things
            response = raw_input('Please Crystallize! Type "f" is not successful and sequence should be terminated')
            if response == 'f':
                return False
            else:
                self.rf.amplitude(T.Value(initpower,'dBm'))
                time.sleep(self.rf_settling_time)
                self.pulser.switch_manual('crystallization',  False)
                time.sleep(self.shutter_delay)
                self.pulser.switch_auto('110DP',  False)
                return True