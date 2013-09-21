import time
import math
from labrad.units import WithUnit

class Crystallizer(object):
    
    '''
    class for handling recrystallization of ion chains
    
    @var thresholdPercentage: percentage of PMT counts below which the ions are considered melted
    @var crystallization_attempts: how many attempts will be made to recrystallize before giving an error
    @var detect_time: how long to record fluorescence to determine crystallation
    @var far_red_time: how long to apply the far red beam while trying to crystalize
    @var optimal_cool_time: duration for both far red and near red lights together
    @var shutter_delay: additional delay for shutter switching
    @var use_rf: boolean to determine whether or not RF should be used to crystallize
    @var rf_crystal_power: power to apply to rf while crystallizing
    @var rf_settling_time: how long to wait for rf power to settle
    
    '''
    thresholdPercentage = 0.9
    crystallization_attempts = 1
    detect_time = WithUnit(0.225 ,'s')
    far_red_time = WithUnit(0.300,'s')
    optimal_cool_time = WithUnit(0.150 ,'s')
    shutter_delay = WithUnit(25, 'ms')
    rf_crystal_power = WithUnit(-7.0, 'dBm')
    rf_settling_time = WithUnit(0.3 , 's')
    
    def __init__(self, pulser, pmt, rf = None):
        self.pulser = pulser
        self.pmt = pmt
        self.rf = rf
        self.crystal_threshold = None

    def get_initial_rate(self):
        signal = self._get_ion_signal()
        self.crystal_threshold = self.thresholdPercentage * signal
#        assert self.crystal_threshold > 0, "Crystalize r: No Ion Signal"
        print 'Crystallizer: Initial Ion Signal {0:.2f} => Threshold {1:.2f}'.format(signal, self.crystal_threshold) 
    
    def _get_ion_signal(self):
        '''
        sets the mode to dfferential, gets background and total signal and returns them
        '''
        pmt_resolution = self.pmt.get_time_length()
        self.pmt.set_mode('Differential')
#        time.sleep(2 * pmt_resolution['s'])
        count_num = int(math.ceil(self.detect_time['s'] / pmt_resolution['s']))
        background = self.pmt.get_next_counts('OFF', count_num , True)
        total = self.pmt.get_next_counts('ON', count_num , True)
        self.pmt.set_mode('Normal')
#        time.sleep(2 * pmt_resolution['s'])
        return total - background
        
    def is_crystallized(self):
        signal = self._get_ion_signal()
        print 'Crystallizer: Current Ion Signal {0:.2f} and Threshold is {1:.2f}'.format(signal, self.crystal_threshold)
        return (signal > self.crystal_threshold) 
    
    def auto_crystallize(self): 
        attempt_counter = 0
        while not self.is_crystallized():
            if attempt_counter > self.crystallization_attempts:
                print 'Failed to Crystallize in {0} attempts'.format(self.crystallization_attempts + 1)
                response = raw_input('Please Crystallize! Type "f" is not successful')
                if response == 'f':
                    return False
                else:
                    return True
            else:
                attempt_counter += 1
                self._do_crystallize()
        print 'Crystallized on attempt', attempt_counter + 1
        return True
        
    def _do_crystallize(self):
        '''
        preforms one attempt of recrystalization
        '''
        #open the far red shutter
        self.pulser.switch_manual('crystallization',  True)
        time.sleep(self.shutter_delay['s'])
        #turn off DP to get all light into far red 0th order
        self.pulser.output('110DP',  False) 
        if self.rf is not None:
            #if provided access to rf, lower the amplitude
            initpower = self.rf.amplitude()
            self.rf.amplitude(self.rf_crystal_power,'dBm')
            time.sleep(self.rf_settling_time['s'])
        time.sleep(self.far_red_time['s'])
        self.pulser.output('110DP',  True) 
        time.sleep(self.optimal_cool_time['s'])
        self.pulser.switch_manual('crystallization',  False)
        time.sleep(self.shutter_delay['s'])
        #go back with the rf settings
        if self.rf is not None:
            self.rf.amplitude(initpower)
            time.sleep(self.rf_settling_time['s'])

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    cr = Crystallizer(cxn.pulser, cxn.normalpmtflow)
    cr.get_initial_rate()
#    print cr.is_crystallized()
    cr.auto_crystallize()