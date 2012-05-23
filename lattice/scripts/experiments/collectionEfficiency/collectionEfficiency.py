import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy
import time
from scriptLibrary import dvParameters 
from PulseSequences.collectionEfficiency import collectionEfficiency
import dataProcessor

repeatitions = 100;
params = {
          'dopplerCooling':50e-3,
          'iterDelay':1e-3,
          'iterationsCycle': 100,
          'repumpD':20.0*10**-6,
          'repumpDelay':10.0*10**-6,
          'exciteP':20.0*10**-6,
          'finalDelay':10.0*10**-6,
              }

experimentName = 'collectionEfficiency'
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

#connect and define servers we'll be using
cxn = labrad.connect()
dv = cxn.data_vault
pulser = cxn.pulser
dp = dataProcessor.dataProcessor(params)
#pulse sequence
pulser.new_sequence()
seq = collectionEfficiency(pulser)
seq.setVariables(**params)
seq.defineSequence()
pulser.program_sequence()
#light logic
pulser.switch_auto('866DP', True) #high TTL means light ON
pulser.switch_auto('110DP', True)
pulser.switch_manual('crystallization', False)
#create directory
dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
for i in range(repeatitions):
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print 'got {0} timetags on iteration {1}'.format(timetags.size, i + 1)
    #saving timetags
    dv.new('timetags iter{0}'.format(i),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
    dv.add_parameter('iteration',i)
    ones = numpy.ones_like(timetags)
    dv.add(numpy.vstack((timetags,ones)).transpose())
    dvParameters.saveParameters(dv, params)
    #data processing on the fuly
    dp.addTimetags(timetags)

#revert the logic
pulser.switch_auto('866DP', False) #high TTL means light Off
pulser.switch_manual('110DP', True)
#complete
print 'SAVED {}'.format(dirappend)
dp.normalize(repeatitions)
dp.makePlot()
print 'DONE'