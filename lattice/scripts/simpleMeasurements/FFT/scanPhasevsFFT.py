from FFT import measureFFT
import numpy as np
import labrad

cxn = labrad.connect()
dv = cxn.data_vault
rs = cxn.rohdeschwarz_server
rs.select_device('lattice-imaging GPIB Bus - USB0::0x0AAD::0x0054::102549')

phaseMin =219.0
phaseMax = 220.0
phaseStep = 0.5
recordTime = 0.5 #seconds
average = 4
freqSpan = 300.0 #Hz 
freqOffset = -310.0 #Hz, the offset between the counter clock and the rf synthesizer clock
#setting up FFT
fft = measureFFT(cxn, recordTime, average, freqSpan, freqOffset, savePlot = False)
#saving
dv.cd(['','QuickMeasurements','FFT'],True)
name = dv.new('FFT',[('Phase', 'deg')], [('FFTPeak','Arb','Arb')] )
dv.add_parameter('plotLive',True)
print 'Saving {}'.format(name)

phases = np.arange(phaseMin, phaseMax + phaseStep, phaseStep)

for phase in phases:
    print 'setting phase {}'.format(phase)
    rs.set_phase(phase)
    micromotion = fft.getPeakArea(ptsAround = 3)
    dv.add(phase, micromotion)