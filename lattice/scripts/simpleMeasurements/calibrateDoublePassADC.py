import labrad
import numpy
import time

'''Calibrates double passes using ADC'''
#servers
cxn = labrad.connect()
dv = cxn.data_vault
dp = cxn.double_pass
adc = cxn.adcserver

#global variables
DOUBLE_PASS = 'axial'; MAX_POWER =5.0 #dBM
MIN_POWER = 0.0    
#DOUBLE_PASS = 'axial'; MAX_POWER =5.0 #dBM
ADCCHANNEL = '4'#DOUBLE_PASS
NUM_STEP_FREQ = 200
AVERAGE_POINTS = 20     #how many output points to average
NUM_STEP_POWER = 200        #dBM
#initialize
dp.select(DOUBLE_PASS)
scanPowerList = numpy.r_[MIN_POWER:MAX_POWER:complex(0,NUM_STEP_POWER)]
#scans the AO frequency at a given power and returns the resulting ADC voltage
def performFreqScan(pwr):
    counts = []
    dp.amplitude(pwr)
    print 'power {}'.format(pwr)
    for freq in scanList:
        dp.frequency(freq)
        output = record(AVERAGE_POINTS)
        counts.append(output)
        print 'measured freq {0}, output {1} mV'.format(freq, output)
    return numpy.array(counts)

#scans the AO power at a given frequency and returns the resulting ADC voltage
def performPowerScan(freq):
    counts = []
    dp.frequency(freq)
    print 'freq {}'.format(freq)
    for pwr in scanPowerList:
        dp.amplitude(pwr)
        output = record(AVERAGE_POINTS)
        counts.append(output)
        print 'measured power {0}, output {1} mV'.format(pwr, output)
    return numpy.array(counts)

def performCalibratedScan(pwr_offset):
    counts = []
    dp.amplitude_offset(pwr_offset)
    for freq in scanList:
        dp.frequency_calibrated_amplitude(freq)
        output = record(AVERAGE_POINTS)
        counts.append(output)
        print 'measured freq {0}, output {1} mV'.format(freq, output)
    return numpy.array(counts)

def record(points):
    result = numpy.zeros(points)
    for j in range(points):
        result[j] = adc.measurechannel(ADCCHANNEL)
    return numpy.average(result)

#lowers the AO power from max to min until the counts decrease to below setpoint
#if not found, returns None
def lowerTillMatches(min, max, setpt):
    STEP_POWER = .05
    for pwr in numpy.arange(max,min -STEP_POWER,-STEP_POWER):  #makes sure that down to and including min power
        dp.amplitude(pwr)
        Output = record(AVERAGE_POINTS)
        if Output < setpt:
            return pwr
    return None

def raiseTillMatches(min,max,setpt):
    STEP_POWER = .05
    for pwr in numpy.arange(min,max + STEP_POWER,STEP_POWER): #makes sure that goes up to and including max power
        dp.amplitude(pwr)
        Output = record(AVERAGE_POINTS)
        if Output > setpt:
            return pwr
    return None

def findPower(guessPower, setpt):
    dp.amplitude(guessPower)
    Output = record(AVERAGE_POINTS)
    print Output
    print setpt
    if Output < setpt:
        print 'raising'
        pwr = raiseTillMatches(guessPower, MAX_POWER, setpt )
    elif Output >= setpt:
        print 'lowering'
        pwr = lowerTillMatches(MIN_POWER, guessPower, setpt )
    return pwr

'''FREQUENCY SCAN'''
def freqScan(power): 
    print 'starting frequency scan'
    scanResult = performFreqScan(power)
    dv.cd(['','Calibrations','Double Pass {}'.format(DOUBLE_PASS)],True)
    dv.new('{0} double pass before calibration, power {1}'.format(DOUBLE_PASS, power ), [('freq','MHz')],[('output','output','arb')])
    data = numpy.vstack((scanList, scanResult)).transpose()
    dv.add(data)  

'''POWER SCAN'''
def powerScan(freq):
    print 'setting the frequency to {} and scanning the power'.format(freq)
    scanResult = performPowerScan(freq)
    dv.cd(['','Calibrations','Double Pass {}'.format(DOUBLE_PASS)],True)
    dv.new('{0} double pass power scan at freq {1}'.format(DOUBLE_PASS, freq ),[('power','dBM')],[('power','power','V')])
    data = numpy.vstack((scanPowerList, scanResult)).transpose()
    dv.add(data)

'''CALIBRATED SCAN'''
def calibratedScan(power_offset):
    print 'starting calibrated scan'
    scanResult = performCalibratedScan(power_offset)
    dv.cd(['','Calibrations','Double Pass {}'.format(DOUBLE_PASS)],True)
    dv.new('{0} calibrated scan offset {1}'.format(DOUBLE_PASS, power_offset ), [('freq','MHz')],[('output','output','arb')])
    data = numpy.vstack((scanList, scanResult)).transpose()
    dv.add(data)  

def calibrateBrute(setPointLevel = 0.9):
    '''PERFORM CALIBRATION using a brute technique of raising or lowering the AO power until the desired level is reached'''
    #scans the frequency and max power
    scanResult = performFreqScan(MAX_POWER)
    minCount = scanResult.min()
    print 'minimum counts are {}'.format(minCount)
    minarg = scanResult.argmin()
    print 'frequency giving least intensity is ', scanResult[minarg]
    setPointCount = minCount * setPointLevel #setting setpoint to 90% of the minimum power
    print 'setting the output set point to ', setPointCount
    calibration = []
    guess = MAX_POWER;
    for freq in scanList:
        print 'calibration freq', freq
        dp.frequency(freq)
        pwr = findPower(guess, setPointCount)
        guess = pwr
        calibration.append([freq, pwr])
    print 'adding to data vault'
    dv.cd(['','Calibrations','Double Pass {}'.format(DOUBLE_PASS)],True)
    dv.new('{0} calibration brute force'.format(DOUBLE_PASS),[('freq','MHz')],[('power','power','dBm')])
    dv.add(calibration)

def calibrateElegant(setPointLevel = 1.0):
    '''Perform calibration using a more elegant technique of first scanning the frequency, then the power at a given frequency'''
    #scanList = numpy.r_[minFreq:maxFreq:complex(0,NUM_STEP_FREQ)]
    #scan power and frequencies separately
    powerScanResult = performPowerScan(centerFreq)
    dv.cd(['','Calibrations','Double Pass {}'.format(DOUBLE_PASS)],True)
    dv.new('{0} double pass power scan at freq {1}'.format(DOUBLE_PASS, centerFreq ),[('power','dBM')],[('power','power','V')])
    data = numpy.vstack((scanPowerList, powerScanResult)).transpose()
    dv.add(data)
    scanFreqResult = performFreqScan(MAX_POWER)
    dv.cd(['','Calibrations','Double Pass {}'.format(DOUBLE_PASS)],True)
    dv.new('{0} double pass before calibration, power {1}'.format(DOUBLE_PASS, MAX_POWER ), [('freq','MHz')],[('output','output','arb')])
    data = numpy.vstack((scanList, scanFreqResult)).transpose()
    dv.add(data)  
    #find setpoint
    minarg = scanFreqResult.argmin()
    minCount = scanFreqResult.min()
    setPointCount = minCount * setPointLevel
    #normalize power scan so that maximum is 1
    print powerScanResult
    print powerScanResult.max()
    powerScanResult = powerScanResult / powerScanResult.max() 
    print powerScanResult
    calibration = []
    for index, freq in enumerate(scanList):
        relativeLevelNeeded = setPointCount / scanFreqResult[index]
        print 'need ', relativeLevelNeeded
        closestPower = scanPowerList[(numpy.abs(powerScanResult - relativeLevelNeeded)).argmin()]
        print 'power ', closestPower
        calibration.append([freq, closestPower])
    print 'adding to data vault'
    dv.cd(['','Calibrations','Double Pass {}'.format(DOUBLE_PASS)],True)
    dv.new('{0} calibration elegant'.format(DOUBLE_PASS),[('freq','MHz')],[('power','power','dBm')])
    dv.add(calibration)
    print calibration
    

MIN_FREQ = 190.0
MAX_FREQ = 250.0   
scanList = numpy.r_[MIN_FREQ:MAX_FREQ:complex(0,NUM_STEP_FREQ)]
centerFreq = (MIN_FREQ + MAX_FREQ)/2.0

#to run:
#powerScan(centerFreq)
calibratedScan(power_offset = 0.0)
freqScan(MAX_POWER)
#calibrateElegant()
#calibrateBrute()
