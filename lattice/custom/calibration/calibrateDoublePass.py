import labrad
import numpy
import time

cxn = labrad.connect()
dv = cxn.data_vault
sigGen = cxn.rohdeschwarz_server
sigGen.select_device('lattice-pc GPIB Bus - USB0::0x0AAD::0x0054::104543')

scope = cxn.tektronix_server
scope.select_device(0) #only works if one tektronix scope is connected
CHANNEL = 1

NUM_STEP_FREQ = 40.0
AVERAGE_POINTS = 1#10 #how many output points to average
MIN_FREQ = 190.0 #MHZ
MAX_FREQ = 250.0 #MHZ
scanList = numpy.r_[MIN_FREQ:MAX_FREQ:complex(0,NUM_STEP_FREQ)]
MAX_POWER = -13.5
MIN_POWER = -20
STEP_POWER = 0.1

#scans the AO frequency and returns the resulting PMT counts at a given power
def performScan(pwr):
    counts = []
    sigGen.amplitude(pwr)
    print 'power {}'.format(pwr)
    for freq in scanList:
        sigGen.frequency(freq)
        Output = record(AVERAGE_POINTS)
        counts.append(Output)
        print 'measured freq {0}, output {1}'.format(freq, Output)
    return numpy.array(counts)

def record(points):
    result = numpy.zeros(points)
    for j in range(points):
        time.sleep(1)
        result[j] = scope.measure(CHANNEL)
    time.sleep(1)
    return numpy.average(result)

#lowers the AO power from max to min until the counts decrease to below setpoint
#if not found, returns None
def lowerTillMatches(min, max, setpt):
    for pwr in numpy.arange(max,min -STEP_POWER,-STEP_POWER):  #makes sure that down to and including min power
        sigGen.amplitude(pwr)
        print 'setting power', pwr
        Output = record(AVERAGE_POINTS)
        print 'in lowering'
        print 'measured', Output
        print 'setpoint was', setpt
        if Output < setpt:
            return pwr
    return None

def raiseTillMatches(min,max,setpt):
    for pwr in numpy.arange(min,max + STEP_POWER,STEP_POWER): #makes sure that goes up to and including max power
        sigGen.amplitude(pwr)
        print 'setting power', pwr
        Output = record(AVERAGE_POINTS)
        if Output > setpt:
            return pwr
    return None

def findPower(guessPower, setpt):
    sigGen.amplitude(guessPower)
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

dv.cd(['','Calibrations'],True)
dv.open(38)
data = dv.get()

dv.new('397 calibrated output',[('freq','MHz')],[('power','power','dBm')])
for point in data:
    freq = point[0]
    power = point[1]
    print 'setting {0}, {1}'.format(freq,power)
    sigGen.frequency(freq)
    sigGen.amplitude(power)
    Output = record(AVERAGE_POINTS)
    dv.add([freq, Output])
    
    
    
#print 'setting power to MAX and scanning the frequency'
#scan = numpy.array(performScan(MAX_POWER))
#dv.cd(['','Calibrations'],True)
#dv.new('397 local probe double pass 3220-120 scan frequency at max power',[('freq','MHz')],[('power','power','dBm')])
#data = numpy.vstack((scanList, scan)).transpose()
#dv.add(data)  
#print 'done'

##POWER SCAN AT FIXED FREQ
#print 'setting the frequency to {} and scanning the power'.format(MIN_FREQ)
#sigGen.frequency(MIN_FREQ)
#dv.cd(['','Calibrations'],True)
#dv.new('397 heating double pass 3080-120 scan power at min freq',[('power','dBM')],[('power','power','V')])
#for pwr in numpy.arange(MIN_POWER,MAX_POWER + STEP_POWER,STEP_POWER):
#    print 'power {}'.format(pwr)
#    sigGen.amplitude(pwr)
#    output = record(AVERAGE_POINTS)
#    dv.add(pwr, output)
#print 'done'
    

##FINDS THE MINIMUM (FREQ./POWER) OF THE SCAN
#print scan
#minCount = scan.min()
#print 'minimum counts are ', minCount
#minarg = scan.argmin()
#print 'frequency giving least intensity is ', scanList[minarg]
#setPointCount = minCount * 0.9 #setting setpoint to 90% of the minimum power
#print 'setting the output set point to ', setPointCount
###
###CALIBRATING
#calibration = []
#guess = MAX_POWER;
#for freq in scanList:
#    print 'calibration freq', freq
#    sigGen.frequency(freq)
#    pwr = findPower(guess, setPointCount)
#    guess = pwr
#    calibration.append([freq, pwr])
#
#print 'final calibration'
#print calibration
#
#print 'adding to data vault'
#dv.cd(['','Calibrations'],True)
#dv.new('397 double pass 3080-120 local beam probe',[('freq','MHz')],[('power','power','dBm')])
#dv.add(calibration)    