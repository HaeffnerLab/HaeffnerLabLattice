import numpy
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import labrad

#DATASET = 400
#steps_c1 = 15
#steps_c2 = 10
#steps_freq = 5

#DATASET = 399
#steps_c1 = 10
#steps_c2 = 10
#steps_freq = 5

#DATASET = 409
#steps_c1 = 15
#steps_c2 = 15
#steps_freq = 5

#DATASET = 448
#steps_c1 = 10
#steps_c2 = 3
#steps_freq = 5

#DATASET = 453
#steps_c1 = 15
#steps_c2 = 15
#steps_freq = 5

DATASET = 455
steps_c1 = 10	
steps_c2 = 10
steps_freq = 5

cxn = labrad.connect()
dv = cxn.data_vault
dv.open(DATASET)
rawdata = numpy.array ( dv.get().asarray )
print 'initial shape'
print rawdata.shape

shapeddata = rawdata.reshape(steps_c1, steps_c2, steps_freq, 5)
print 'now reshaping'
print shapeddata.shape


diffarray = numpy.zeros([steps_c1,steps_c2])
c1array = numpy.zeros([steps_c1,steps_c2])
c2array = numpy.zeros([steps_c1,steps_c2])
backgndarray = numpy.zeros([steps_c1,steps_c2])
PMTonArray = numpy.zeros([steps_c1,steps_c2])

for i in range(steps_c1):
  for j in range(steps_c2):
    c1 = shapeddata[i][j][0][0]
    c2 = shapeddata[i][j][0][1]
    rfoffline = shapeddata[i][j][:].transpose()[3]
    rfonline = shapeddata[i][j][:].transpose()[4]
    diffline = rfonline - rfoffline
    rfoff = numpy.average(rfoffline)
    rfon = numpy.average(rfonline)
    #diff = rfon - rfoff
    maxpos = numpy.argmax(numpy.abs(diffline))
    signofdiff = numpy.sign(diffline)
    diff = diffline[maxpos] #returns the element with largest absolute value
    diffarray[i][j] = diff
    c1array[i][j] = c1
    c2array[i][j] = c2
    backgndarray[i][j] = rfoff
    PMTonArray[i][j] = rfon

#plt.figure(0)
#
#plt.plot(diffline)

plt.figure(1)
CS = plt.contourf(c1array,c2array, backgndarray)
cbar = plt.colorbar(CS)
#c1line =[-214,-266,-276,-295,-311,-328.8,-346,-369, -388.9,-408]
#c2line =[-331,-428,-447,-482,-514,-548,  -581,-623,-660,-697]
#plt.plot(c1line,c2line)

plt.figure(2)
CS = plt.contourf(c1array,c2array, diffarray, 20)
cbar = plt.colorbar(CS)
#c1line =[-214,-266,-276,-295,-311,-328.8,-346,-369, -388.9,-408]
#c2line =[-331,-428,-447,-482,-514,-548,  -581,-623,-660,-697]
#plt.plot(c1line,c2line)

#plt.figure(3)
#CS = plt.contourf(c1array,c2array, PMTonArray)
#cbar = plt.colorbar(CS)
#c1line =[-214,-266,-276,-295,-311,-328.8,-346,-369, -388.9,-408]
#c2line =[-331,-428,-447,-482,-514,-548,  -581,-623,-660,-697]

#plt.plot(c1line,c2line)

plt.show()