import time
#from labrad import types as T
class FrequencyCorrector():
    
    chanName = '397'
    proximityPercentage = 0.05
    detect_time = 0.225
    pmtresolution = 0.075
    timeout = 10 # seconds
    
    def __init__(self, pmt, laserdac):
        self.pmt = pmt
        self.laserdac = laserdac
        self.initial_rate = None

    def get_initial_rate(self):
        self.pmt.set_time_length(self.pmtresolution)
        countNum = int(self.detect_time / self.pmtresolution)
        countRate = self.pmt.get_next_counts('ON', countNum , True)
        self.initial_rate = countRate
        print 'Frequency Corrector: Initial Count Rate {0:.2f}'.format(countRate) 
        
    def is_within_proximity(self):
        countNum = int(self.detect_time / self.pmtresolution)
        countRate = self.pmt.get_next_counts('ON', countNum , True)
        proximity = countRate * self.proximityPercentage
        print 'Frequency Corrector: Count rate {0:.2f} and range is between {1:.2f} and {1:.2f}'.format(countRate, (countRate - proximity), (countRate + proximity))
        return ((countRate > (countRate - proximity)) and (countRate < (countRate + proximity))) 
    
    def get_rate(self):
        countNum = int(self.detect_time / self.pmtresolution)
        countRate = self.pmt.get_next_counts('ON', countNum , True)
        return countRate
    
    def auto_correct(self):       
        if self.is_within_proximity():
            print 'Initially Corrected for Frequency'
            return True
        else:
            print 'Frequency Drift'
            currentVoltage = self.laserdac.getvoltage(self.chanName)
            print 'Initial Voltage: ', currentVoltage
            initialVoltage = currentVoltage          
            timeStart = time.clock()
            time = time.clock()
            
            while((time - timeStart) < self.timeout):
                countRate = self.get_rate()
                if (countRate > self.initial_rate):
                    # up the voltage
                    currentVoltage += 1
                    self.laserdac.setvoltage(self.chanName, currentVoltage)
                    print 'Current Voltage: ', currentVoltage
                    if self.is_within_proximity():
                        print 'Frequency Corrected. Cavity changed by ', (currentVoltage - initialVoltage), ' mV.'
                        return True
                else:
                    # down the voltage
                    currentVoltage -= 1
                    self.laserdac.setvoltage(self.chanName, currentVoltage)
                    print 'Current Voltage: ', currentVoltage
                    if self.is_within_proximity():
                        print 'Frequency Corrected. Cavity changed by ', (currentVoltage - initialVoltage), ' mV.'
                        return True
                       
                time = time.clock()          
            
            print 'Failed to bring countrate within range.'    
                