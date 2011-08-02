import labrad
import numpy

cxn = labrad.connect()
sigGen = cxn.lattice_pc_rs_server_blue
dv = cxn.data_vault
pmt = cxn.pmt_server

NUM_STEP_FREQ =30
AVERAGE_POINTS = 10#10 #how many PMT counts to get at each point
MIN_FREQ = 70.0 #MHZ
MAX_FREQ = 90.0 #MHZ
DECREASE_POWER =  3 #same as calibration
scanList = numpy.r_[MIN_FREQ:MAX_FREQ:complex(0,NUM_STEP_FREQ)]

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

dv.cd([''])
dv.new('397 double pass 3080-120 scan',[('freq','MHz')],[('counts','counts','KC/sec')])
for freq in scanList:
    sigGen.setfreq(freq)
    pwr = func2(freq) - DECREASE_POWER
    #pwr = 21.5
    print freq
    print pwr
    assert pwr < 22
    sigGen.setpower(pwr)
    arr = pmt.getnextreadings(AVERAGE_POINTS)
    newCnt = numpy.average(numpy.transpose(arr)[1])
    dv.add([freq,newCnt])
    
   

    