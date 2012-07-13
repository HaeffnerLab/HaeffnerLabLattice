from FFT import measureFFT
import numpy as np
import labrad
from labrad import types as T

cxn = labrad.connect()
dv = cxn.data_vault
rs = cxn.rohdeschwarz_server
rs.select_device('lattice-imaging GPIB Bus - USB0::0x0AAD::0x0054::102549')

amplMin = 0.0
amplMax = 28.0
amplStep = 2.0
recordTime = 0.5 #seconds
average = 4
freqSpan = 300.0 #Hz 
freqOffset = -310.0 #Hz, the offset between the counter clock and the rf synthesizer clock
#setting up FFT
fft = measureFFT(cxn, recordTime, average, freqSpan, freqOffset, savePlot = False)
#saving
dv.cd(['','QuickMeasurements','FFT'],True)
name = dv.new('FFT',[('Amplitude', 'dBm')], [('FFTPeak','Arb','Arb')] )
dv.add_parameter('plotLive',True)
print 'Saving {}'.format(name)

amplitudes = np.arange(amplMin, amplMax + amplStep, amplStep)

initampl = rs.amplitude()
for ampl in amplitudes:
    rs.amplitude(T.Value(ampl, 'dBm'))
    micromotion = fft.getPeakArea(ptsAround = 3)
    dv.add(ampl, micromotion)
rs.amplitude(initampl)