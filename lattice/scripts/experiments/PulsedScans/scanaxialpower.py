import sys 
import numpy as np
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
from scriptLibrary import dvParameters 
from PulseSequences.pulsedScan import PulsedScan
import time
import dataProcessor

minpower = -20.0
maxpower = 5.0
steps = 75
powers = np.linspace(minpower, maxpower, steps)
#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect() #connection to labwide network
dv = cxn.data_vault
dpass = cxn.double_pass
axial = cxn.lattice_pc_hp_server
initpower = axial.amplitude()
pulser = cxn.pulser
experimentName = 'pulsedScanAxialPower'
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

params = {
          'coolingTime':20.0*10**-3,
          'switching':1.0*10**-3,
          'pulsedTime':1.0*10**-3,
          'iterations':100,
        }

def initialize():
    #pulser sequence 
    seq = PulsedScan(pulser)
    pulser.new_sequence()
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    #make sure 110 dpass is on
    dpass.select('110DP')
    dpass.output(True)
    axial.output(True)
    #set logic
    pulser.switch_auto('axial',  True) #high TTL corresponds to light ON
    pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
    pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
    pulser.switch_manual('crystallization',  False) #high TTL corresponds to light OFF
    #set up data vault

    dv.cd(['','Experiments', experimentName, dirappend], True)
    dv.new('timetags',[('Power', 'dBm')],[('TimeTag','Sec','Sec')] )
    dvParameters.saveParameters(dv, params)
    dv.add_parameter('cycleTime', seq.parameters.cycleTime )
    
def sequence():
    for i,pwr in enumerate(powers):
        axial.amplitude(pwr)
        pulser.reset_timetags()
        pulser.start_single()
        pulser.wait_sequence_done()
        pulser.stop_sequence()
        timetags = pulser.get_timetags().asarray
        print 'got {0} timetags on iteration {1}'.format(timetags.size, i + 1)
        print 'power {}'.format(pwr)
        pwrs = np.ones_like(timetags) * pwr
        dv.add(np.vstack((pwrs,timetags)).transpose())
        
def finalize():
    for name in ['axial', '110DP']:
        pulser.switch_manual(name)
    pulser.switch_manual('crystallization',  True)
    axial.amplitude(initpower)

def process():
    dv.open(1)
    data = dv.get().asarray
    params = dict(dv.get_parameters())
    dp = dataProcessor.dataProcessor(params)
    dp.addData(data)
    dp.process()
    dp.makePlot()
    
initialize()
sequence()
finalize()
print 'DONE {}'.format(dirappend)
process()
