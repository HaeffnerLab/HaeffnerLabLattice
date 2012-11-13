import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy
import time
from scriptLibrary import dvParameters 
from PulseSequences.thermalization import thermalization
''''
This experiment studies how the ion heats up. After initial cooling it is repeatedly interrogated with an on resonance beam.
'''
iterations = 1000
pulsePeriod = 1.0 #second

#connect and define servers we'll be using
cxn = labrad.connect()
dv = cxn.data_vault
dpass = cxn.double_pass
pulser = cxn.pulser
#data saving
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
dv.cd(['','Experiments', 'thermalization', dirappend], True )
dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
dv.add_parameter('plotLive',True)
#pulse sequence
pulser.new_sequence()
params = {
            'probe_on':1e-3,
        }
seq = thermalization(pulser)
seq.setVariables(**params)
seq.defineSequence()
pulser.program_sequence()
pulser.switch_auto('866DP', True) #high TTL means light ON
pulser.switch_manual('110DP', False)
pulser.switch_manual('crystallization', False)

for i in range(iterations):
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print 'got {} timetags'.format(timetags.size)
    dv.add([i, timetags.size])
    time.sleep(pulsePeriod)
print 'DONE'