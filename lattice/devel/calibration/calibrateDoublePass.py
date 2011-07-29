import labrad
import numpy

cxn = labrad.connect()
sigGen = cxn.lattice_pc_rs_server_blue
dv = cxn.data_vault
pmt = cxn.pmt_server

NUM_STEP_FREQ =15
AVERAGE_POINTS = 3#10 #how many PMT counts to get at each point
MIN_FREQ = 70.0 #MHZ
MAX_FREQ = 90.0 #MHZ
scanList = numpy.r_[MIN_FREQ:MAX_FREQ:complex(0,NUM_STEP_FREQ)]
MAX_POWER = 21.5
MIN_POWER = 10.0
STEP_POWER = 0.1
count_margin = 1 #the set point of the calibration 90% of least intensity

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
    
    
print 'performing initial scan at maximum power'
PMTcountList = numpy.array(performScan(MAX_POWER))
print PMTcountList
minCount = PMTcountList.min()
print 'minimum counts are ', minCount
minarg = PMTcountList.argmin()
print 'frequency giving least intensity is ', scanList[minarg]
setPointCount = minCount * count_margin
print 'setting the PMT counts set point to ', setPointCount


#lowers the AO power from max to min until the counts decrease to below setpoint
#if not found, returns None
def lowerTillMatches(max, min, setpt):
    for pwr in numpy.arange(max,min,-STEP_POWER):
        sigGen.setpower(pwr)
        print 'setting power', pwr
        arr = pmt.getnextreadings(AVERAGE_POINTS)
        newCnt = numpy.average(numpy.transpose(arr)[1])
        if newCnt < setpt:
            return pwr
    return None


calibration = []
for freq in scanList:
    print 'calibration freq', freq
    sigGen.setfreq(freq)
    pwr = lowerTillMatches(MAX_POWER, MIN_POWER,setPointCount)
    calibration.append([freq, pwr])

print 'final calibration'
print calibration

print 'adding to data vault'
dv.cd(['','Calibrations'],True)
dv.new('397 double pass 3080-120',[('freq','MHz')],[('power','power','dBm')])
dv.add(calibration)    
    
    