import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy
import time
from scriptLibrary import dvParameters 
from PulseSequences.collectionEfficiency import collectionEfficiency

iterations = 100;
params = {
          'dopplerCooling':100e-3,
          'iterDelay':1e-3,
          'iterationsCycle': 250,
          'repumpD':5.0*10**-6,#
          'repumpDelay':5.0*10**-6,
          'exciteP':5.0*10**-6,
          'finalDelay':5.0*10**-6,
              }
experimentName = 'collectionEfficiency'
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

#connect and define servers we'll be using
cxn = labrad.connect()
dv = cxn.data_vault
pulser = cxn.pulser
#pulse sequence
pulser.new_sequence()
seq = collectionEfficiency(pulser)
seq.setVariables(**params)
seq.defineSequence()
pulser.program_sequence()
#light logic
pulser.switch_auto('866DP', True) #high TTL means light ON
pulser.switch_manual('crystallization', False)
pulser.switch_auto('110DP', True)
#data processing on the fly
repumpD = params['repumpD']
repumpDelay = params['repumpDelay']
exciteP = params['exciteP']
finalDelay = params['finalDelay']
dopplerCooling = params['dopplerCooling']
cycleTime = repumpD + repumpDelay + exciteP + finalDelay
binTime = 40.0*10**-9 #fpga resolution

binNumber = int(cycleTime / binTime)
bins = binTime * numpy.arange(binNumber + 1)
binned = numpy.zeros(binNumber)
#data processing on the fly
dopplerBinTime = 1.0*10**-3
dopplerBinNumber = int(dopplerCooling / dopplerBinTime)
dopplerBins = dopplerBinTime * numpy.arange(dopplerBinNumber + 1)
dopplerBinned = numpy.zeros(dopplerBinNumber)

for i in range(iterations):
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print 'got {0} timetags on iteration {1}'.format(timetags.size, i + 1)
    #saving timetags
    dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
    dv.new('timetags iter{0}'.format(i),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
    dv.add_parameter('iteration',i)
    ones = numpy.ones_like(timetags)
    dv.add(numpy.vstack((timetags,ones)).transpose())
    dvParameters.saveParameters(dv, params)

#revert the logic
pulser.switch_auto('866DP', False) #high TTL means light Off
pulser.switch_manual('110DP', True)
print 'DONE {}'.format(dirappend)