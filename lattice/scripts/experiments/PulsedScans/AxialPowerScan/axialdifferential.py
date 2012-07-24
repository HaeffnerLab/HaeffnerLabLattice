import numpy as np
import labrad
from scripts.scriptLibrary import dvParameters 
from scripts.PulseSequences.pulsedScan import PulsedScan
import time
import dataProcessor

#connect and define servers we'll be using
cxn = labrad.connect()
dv = cxn.data_vault
pulser = cxn.pulser
experimentName = 'pulsedAxialDifferential'
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

params = {
          'coolingTime':5.0*10**-3,
          'switching':500.0*10**-9,
          'pulsedTime':1.0*10**-3,
          'iterations':50,
        }

repeatitions = 1000

coolingTime = params['coolingTime']
switching = params['switching']
pulsedTime = params['pulsedTime']
iterations = params['iterations']
cycleTime = None

def initialize():
    global cycleTime
    #pulser sequence 
    seq = PulsedScan(pulser)
    pulser.new_sequence()
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()

    pulser.switch_auto('axial',  True) #high TTL corresponds to light ON
    pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
    pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
    pulser.switch_manual('crystallization',  False) #high TTL corresponds to light OFF
    #set up data vault

    dv.cd(['','Experiments', experimentName, dirappend], True)
    dv.new('fluorDiff',[('Iterations', 'Arb')],[('Counts','Counts / Sec','Counts / Sec')] )
    params['cycleTime'] = seq.parameters.cycleTime
    params['plotLive'] = True
    cycleTime = params['cycleTime']
    dvParameters.saveParameters(dv, params)
    
def finalize():
    for name in ['axial', '110DP']:
        pulser.switch_manual(name)
    pulser.switch_manual('crystallization',  True)
    
def sliceArr(arr, start, duration, cyclenumber = 1, cycleduration = 0 ):
    '''Takes a np array arr, and returns a new array that consists of all elements between start and start + duration modulo the start time
    If cyclenumber and cycleduration are provided, the array will consist of additional slices taken between start and 
    start + duration each offset by a cycleduration. The additional elements will added modulo the start time of their respective cycle'''
    starts = [start + i*cycleduration for i in range(cyclenumber)]
    criterion = reduce(np.logical_or, [(start <= arr) & (arr <=  start + duration) for start in starts])
    result = arr[criterion]
    if cycleduration == 0:
        if start != 0:
            result = np.mod(result, start)
    else:
        result = np.mod(result - start, cycleduration)
    return result

def process(tags):
    countsBackground = sliceArr(tags,  start = coolingTime + switching, duration =  pulsedTime, cyclenumber = iterations, cycleduration = cycleTime)
    countsSignal = sliceArr(tags,  start = coolingTime + switching + pulsedTime, duration = pulsedTime, cyclenumber = iterations, cycleduration = cycleTime)
    collectionTime = pulsedTime * iterations
    diff = (countsSignal.size - countsBackground.size) / float(collectionTime)
    return diff
    #return countsSignal.size - countsBackground.size

def sequence():
    for r in range(repeatitions):
        t = time.time()
        pulser.reset_timetags()
        pulser.start_single()
        pulser.wait_sequence_done()
        pulser.stop_sequence()
        timetags = pulser.get_timetags().asarray
        print time.time() - t
        print 'got {0} timetags on repeatition {1}'.format(timetags.size, r + 1)
        diff = process(timetags)
        dv.add([r, diff])
    
initialize()
sequence()
finalize()