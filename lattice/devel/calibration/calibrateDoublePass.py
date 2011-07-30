import labrad
import numpy

cxn = labrad.connect()
sigGen = cxn.lattice_pc_rs_server_blue
dv = cxn.data_vault
pmt = cxn.pmt_server

NUM_STEP_FREQ =15
AVERAGE_POINTS = 10#10 #how many PMT counts to get at each point
MIN_FREQ = 70.0 #MHZ
MAX_FREQ = 90.0 #MHZ
scanList = numpy.r_[MIN_FREQ:MAX_FREQ:complex(0,NUM_STEP_FREQ)]
MAX_POWER = 21.5
MIN_POWER = 10.0
STEP_POWER = 0.1

#scans the AO frequency and returns the resulting PMT counts
def performScan(pwr):
    counts = []
    sigGen.setpower(pwr)
    for freq in scanList:
        sigGen.setfreq(freq)
        arr = pmt.getnextreadings(AVERAGE_POINTS)
        newCnt = numpy.average(numpy.transpose(arr)[1])
        counts.append(newCnt)
    return counts

def func(x):
    import math
    a1=2.461e24
    b1=-1223
    c1=176.5
    a2=2.165e10
    b2=1246
    c2=252.2
    f = a1*math.exp(-((x-b1)/c1)**2) + a2*math.exp(-((x-b2)/c2)**2)
    return f

def func2(x):
    import math
    a1=2.475e12
    b1=-78.72
    c1=28.64
    a2=37.59
    b2=134
    c2=51.51
    a3=8.113
    b3=70.38
    c3=12.07
    f = a1*math.exp(-((x-b1)/c1)**2) + a2*math.exp(-((x-b2)/c2)**2) + a3*math.exp(-((x-b3)/c3)**2)
    return f

for freq in scanList:
    sigGen.setfreq(freq)
    pwr = func2(freq)
    print freq
    print pwr
    sigGen.setpower(pwr)
    arr = pmt.getnextreadings(AVERAGE_POINTS)
    newCnt = numpy.average(numpy.transpose(arr)[1])


    
print 'performing initial scan at maximum power'
PMTcountList = numpy.array(performScan(MAX_POWER))
print PMTcountList
minCount = PMTcountList.min()
print 'minimum counts are ', minCount
minarg = PMTcountList.argmin()
print 'frequency giving least intensity is ', scanList[minarg]
setPointCount = minCount
print 'setting the PMT counts set point to ', setPointCount


#lowers the AO power from max to min until the counts decrease to below setpoint
#if not found, returns None
def lowerTillMatches(min, max, setpt):
    for pwr in numpy.arange(max,min,-STEP_POWER):
        sigGen.setpower(pwr)
        print 'setting power', pwr
        arr = pmt.getnextreadings(AVERAGE_POINTS)
        newCnt = numpy.average(numpy.transpose(arr)[1])
        print 'in lowering'
        print 'measured', newCnt
        print 'setpoint was', setpt
        if newCnt < setpt:
            return pwr
    return None

def raiseTillMatches(min,max,setpt):
    for pwr in numpy.arange(min,max,STEP_POWER):
        sigGen.setpower(pwr)
        print 'setting power', pwr
        arr = pmt.getnextreadings(AVERAGE_POINTS)
        newCnt = numpy.average(numpy.transpose(arr)[1])
        if newCnt > setpt:
            return pwr
    return None

def findPower(guessPower, setpt):
    sigGen.setpower(guessPower)
    guessCnts = pmt.getnextreadings(AVERAGE_POINTS)
    guessCnts = numpy.average(numpy.transpose(guessCnts)[1])
    print guessCnts
    print setpt
    if guessCnts < setpt:
        print 'raising'
        pwr = raiseTillMatches(guessPower, MAX_POWER, setpt )
    elif guessCnts >= setpt:
        print 'lowering'
        pwr = lowerTillMatches(MIN_POWER, guessPower, setpt )
    return pwr
    
calibration = []
guess = MAX_POWER;
for freq in scanList:
    print 'calibration freq', freq
    sigGen.setfreq(freq)
    pwr = findPower(guess, setPointCount)
    guess = pwr
    calibration.append([freq, pwr])

print 'final calibration'
print calibration

print 'adding to data vault'
dv.cd(['','Calibrations'],True)
dv.new('397 double pass 3080-120',[('freq','MHz')],[('power','power','dBm')])
dv.add(calibration)    

def func(x):
    import math
    a1=2.461e24
    b1=-1223
    c1=176.5
    a2=2.165e10
    b2=1246
    c2=252.2
    f = a1*math.exp(-((x-b1)/c1)**2) + a2*math.exp(-((x-b2)/c2)**2)
    return f


    