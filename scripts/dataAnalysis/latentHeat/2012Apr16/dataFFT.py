# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 19:59:17 2012

@author: lattice
"""

import numpy
import labrad
import sys
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot
from scripts.simpleMeasurements.FFT.FFT import measureFFT

totalTraces = 1
datasets = ['2012Apr16_2000_11']


refSigs = []
detectedCounts = [] #list of counts detected during readout
freqSpan = 300.0 #Hz (for FFT)
freqOffset = -310.0 #Hz, the offset between the counter clock and the rf synthesizer clock

for datasetName in datasets:
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    xtal_record = dv.get_parameter('xtal_record')
    pulse_length = initial_cooling + heat_delay + axial_heat + readout_delay + readout_time + xtal_record
#    
    # readout range
    heatStart = (initial_cooling + heat_delay ) # / 10.0**6 #in seconds
    heatEnd = (initial_cooling + heat_delay +axial_heat ) 
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay ) 
    stopReadout = startReadout + readout_time 
    print datasetName#, heatStart, heatEnd, startReadout, stopReadout
    print 'Readout time :', stopReadout - startReadout
    print 'Heating time :', heatEnd - heatStart
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])     

    for dataset in range(1,totalTraces+1):
        micromotion = []
        dv.open(int(dataset))
        timetag = dv.get().asarray[:,0]
        Readout = ((startReadout <= timetag) * (timetag <= stopReadout))
        tags = timetag[Readout]
        #counts0 = numpy.count_nonzero((startReadout <= tags2) * (tags2 <= stopReadout))
        fft = measureFFT(cxn, float(pulse_length), totalTraces, freqSpan, freqOffset, savePlot = True)       
        #micromotion = fft.getPeakArea(ptsAround = 3)        
        micromotion = fft.getFFTpwr(timetags = tags)
        fft.saveData(micromotion)
        #countsReadout = numpy.count_nonzero((startReadout <= tags) * (tags <= stopReadout))
        #detectedCounts.append(countsReadout)
print numpy.shape(micromotion)
    
print 'Done'
#pyplot.hist(detectedCounts, 60)
#pyplot.show()