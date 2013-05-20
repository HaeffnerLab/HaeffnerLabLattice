import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

dv.cd(['','QuickMeasurements','FFT'])
dv.open(1460)
data=dv.get()
data = numpy.transpose(data)  # transposed
x = data[0]; 
y = data[1];
x2 = numpy.linspace(0,8000,100)
y2 = -5.1e-4*x2 + 3.8

figure = pyplot.figure()
figure.clf()
pyplot.plot(x,y*1e5,'o')
pyplot.hold('True')
pyplot.plot(x2,y2)
pyplot.xlabel('Compensation (V)')
pyplot.ylabel('FFT signal (arb)')

# need ~ 7.5 kV
