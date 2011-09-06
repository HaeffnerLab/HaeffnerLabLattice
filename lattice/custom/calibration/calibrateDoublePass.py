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

NUM_STEP_FREQ = 5
AVERAGE_POINTS = 1#10 #how many ouput points to average
MIN_FREQ = 190.0 #MHZ
MAX_FREQ = 250.0 #MHZ
scanList = numpy.r_[MIN_FREQ:MAX_FREQ:complex(0,NUM_STEP_FREQ)]
MAX_POWER = -13.5
MIN_POWER = -30
STEP_POWER = 0.5

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
        print 'measured {}'.format(result[j])
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

print 'performing initial scan at maximum power'
scan = numpy.array(performScan(MAX_POWER))
print scan
minCount = scan.min()
print 'minimum counts are ', minCount
minarg = scan.argmin()
print 'frequency giving least intensity is ', scanList[minarg]
setPointCount = minCount * 0.9 #setting setpoint to 90% of the minimum power
print 'setting the output set point to ', setPointCount

calibration = []
guess = MAX_POWER;
for freq in scanList:
    print 'calibration freq', freq
    sigGen.frequency(freq)
    pwr = findPower(guess, setPointCount)
    guess = pwr
    calibration.append([freq, pwr])

print 'final calibration'
print calibration

print 'adding to data vault'
dv.cd(['','Calibrations'],True)
dv.new('397 double pass 3080-120 local beam probe',[('freq','MHz')],[('power','power','dBm')])
dv.add(calibration)    

#def func(x):
#    import math
#    a1=2.461e24
#    b1=-1223
#    c1=176.5
#    a2=2.165e10
#    b2=1246
#    c2=252.2
#    f = a1*math.exp(-((x-b1)/c1)**2) + a2*math.exp(-((x-b2)/c2)**2)
#    return f

#def func(x):
#    import math
#    a1=2.461e24
#    b1=-1223
#    c1=176.5
#    a2=2.165e10
#    b2=1246
#    c2=252.2
#    f = a1*math.exp(-((x-b1)/c1)**2) + a2*math.exp(-((x-b2)/c2)**2)
#    return f
#
#def func2(x):
#    import math
#    a1=2.475e12
#    b1=-78.72
#    c1=28.64
#    a2=37.59
#    b2=134
#    c2=51.51
#    a3=8.113
#    b3=70.38
#    c3=12.07
#    f = a1*math.exp(-((x-b1)/c1)**2) + a2*math.exp(-((x-b2)/c2)**2) + a3*math.exp(-((x-b3)/c3)**2)
#    return f

#for freq in scanList:
#    sigGen.frequency(freq)
#    pwr = func2(freq)
#    print freq
#    print pwr
#    sigGen.setpower(pwr)
#    arr = pmt.getnextreadings(AVERAGE_POINTS)
#    newCnt = numpy.average(numpy.transpose(arr)[1])    