import sys 
import numpy as np
#sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
#sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
#from scriptLibrary import dvParameters 
#from PulseSequences.collectionEfficiency import collectionEfficiency
#import dataProcessor

repeatitions = 100;

frequency = 250.0
minpower = -30.0
maxpower = 5.0
steps = 20
#creating the RS list
powers = np.linspace(minpower, maxpower, steps)
rs220List = [(frequency, pwr) for pwr in powers]

#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
dv = cxn.data_vault
dpass = cxn.double_pass
rs220DP = cxn.rohdeschwarz_server
pulser = cxn.pulser
experimentName = 'pulsedScanAxialPower'

params = {
          'coolingTime':10.0*10**-3,
          'switching':2.0*10**-3,
          'pulsedTime':100*10**-6,
          'pulsedSteps':steps,
          'iterationsCycle':10,
        }

def initialize():
    #pulser sequence 
    seq = PulsedScan(pulser)
    pulser.new_sequence()
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
