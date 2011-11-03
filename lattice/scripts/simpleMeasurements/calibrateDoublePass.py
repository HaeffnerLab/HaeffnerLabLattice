import labrad
import numpy
import time

#calibrates the doulbe pass using ADC

#servers
cxn = labrad.connect()
dv = cxn.data_vault
dp = cxn.double_pass
adc = cxn.adcserver

#global variables
DOUBLE_PASS = 'axial'; dp.select(DOUBLE_PASS)
CHANNEL = 1
NUM_STEP_FREQ = 40
AVERAGE_POINTS = 10#10 #how many output points to average
MIN_FREQ = 190.0 #MHZ
MAX_FREQ = 250.0 #MHZ
scanList = numpy.r_[MIN_FREQ:MAX_FREQ:complex(0,NUM_STEP_FREQ)]
MAX_POWER = 5.0
MIN_POWER = -40
STEP_POWER = 0.1
DELAY_UPDATE = 0.0
DELAY_AVERAGE = 0.0

#scans the AO frequency and returns the resulting PMT counts at a given power
def performScan(pwr):
    counts = []
    dp.amplitude(pwr)
    print 'power {}'.format(pwr)
    for freq in scanList:
        dp.frequency(freq)
        time.sleep(DELAY_UPDATE)
        Output = record(AVERAGE_POINTS)
        counts.append(Output)
        print 'measured freq {0}, output {1} mV'.format(freq, Output)
    return numpy.array(counts)

def performCalibratedScan(pwr_offset):
    counts = []
    dp.amplitude_offset(pwr_offset)
    for freq in scanList:
        dp.frequency_calibrated_amplitude(freq)
        time.sleep(DELAY_UPDATE)
        Output = record(AVERAGE_POINTS)
        counts.append(Output)
        print 'measured freq {0}, output {1} mV'.format(freq, Output)
    return numpy.array(counts)

def record(points):
    result = numpy.zeros(points)
    for j in range(points):
        result[j] = adc.measurechannel(CHANNEL)
        time.sleep(DELAY_AVERAGE)
    return numpy.average(result)

#lowers the AO power from max to min until the counts decrease to below setpoint
#if not found, returns None
def lowerTillMatches(min, max, setpt):
    for pwr in numpy.arange(max,min -STEP_POWER,-STEP_POWER):  #makes sure that down to and including min power
        dp.amplitude(pwr)
        Output = record(AVERAGE_POINTS)
        if Output < setpt:
            return pwr
    return None

def raiseTillMatches(min,max,setpt):
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


print 'frequency scan'
scan = numpy.array(performScan(MAX_POWER))
dv.cd(['','Calibrations'],True)
dv.new('{0} double pass before calibration, power {1}'.format(DOUBLE_PASS, MAX_POWER ), [('freq','MHz')],[('output','output','arb')])
data = numpy.vstack((scanList, scan)).transpose()
dv.add(data)  
print 'done'

print 'calibrated scan'
power_offset = 0.0
scan = numpy.array(performCalibratedScan(power_offset))
dv.cd(['','Calibrations'],True)
dv.new('{0} calibrated scan offset {1}'.format(DOUBLE_PASS, power_offset ), [('freq','MHz')],[('output','output','arb')])
data = numpy.vstack((scanList, scan)).transpose()
dv.add(data)  
print 'done'

#print 'setting the frequency to {} and scanning the power'.format(MIN_FREQ)
#dp.frequency(MIN_FREQ)
#dv.cd(['','Calibrations'],True)
#dv.new('{0} double pass power scan at freq {1}'.format(DOUBLE_PASS, MIN_FREQ ),[('power','dBM')],[('power','power','V')])
#for pwr in numpy.arange(MIN_POWER,MAX_POWER,STEP_POWER):
#    print 'power {}'.format(pwr)
#    dp.amplitude(pwr)
#    output = record(AVERAGE_POINTS)
#    dv.add(pwr, output)
#print 'done'
#    
#
##FINDS THE MINIMUM (FREQ./POWER) OF THE SCAN
#print scan
#minCount = scan.min()
#print 'minimum counts are ', minCount
#minarg = scan.argmin()
#print 'frequency giving least intensity is ', scanList[minarg]
#setPointCount = minCount * 0.9 #setting setpoint to 90% of the minimum power
#print 'setting the output set point to ', setPointCount
#
#print 'calibrating'
#calibration = []
#guess = MAX_POWER;
#for freq in scanList:
#    print 'calibration freq', freq
#    dp.frequency(freq)
#    pwr = findPower(guess, setPointCount)
#    guess = pwr
#    calibration.append([freq, pwr])
#
#print 'adding to data vault'
#dv.cd(['','Calibrations'],True)
#dv.new('{0} calibration'.format(DOUBLE_PASS),[('freq','MHz')],[('power','power','dBm')])
#dv.add(calibration)    