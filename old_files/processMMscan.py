
import numpy
import matplotlib
#matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import labrad
##fill these in automatically in the future

DATASET = 400
steps_c1 = 15
steps_c2 = 10
steps_freq = 5

cxn = labrad.connct()
dv = cxn.data_vault
dv.open(DATASET)
rawdata = numpy.array ( dv.get().asarray )
print 'hi'
print rawdata.shape

#filepath = '/home/micramm/micromotionfreqscan75raw.npy'

#steps_c1 = 2
#steps_c2 = 21
#steps_freq = 36
#filepath = '/home/micramm/micromotionfreqscan76raw.npy'

#steps_c1 = 6
#steps_c2 = 6
#steps_freq = 18
#filepath = '/home/micramm/micromotionfreqscan78raw.npy'

#steps_c1 = 6
#steps_c2 = 6
#steps_freq = 54
#filepath = '/home/micramm/data.npy'

#steps_c1 = 2
#steps_c2 = 2
#steps_freq = 2
#filepath = '/home/micramm/file.npy'

#rainbowlistred = [[float(i+1)/(steps_c2/3.),0,0] for i in range(int(round(steps_c2/3.)))]
#rainbowlistgreen = [[0,float(i+1)/(steps_c2/3.),0] for i in range(int(round(steps_c2/3.)))]
#raindbowlistblue = [[0,0,float(i+1)/(steps_c2/3.)] for i in range(int(round(steps_c2/3.)))]
#rainbowlistgreen.extend(raindbowlistblue)
#rainbowlistred.extend(rainbowlistgreen)

#try:
	#rawdata = numpy.load(filepath)
#except IOError:
	#print 'File could not be found, wrong path'
	#exit()
#print 'loaded file of length', len(rawdata)
#elementlength =  len(rawdata[0])
#print 'each element has length', elementlength

#data = numpy.reshape(rawdata,(steps_c1, steps_c2, steps_freq, elementlength))
#print 'reshaping', numpy.shape(rawdata),'to', numpy.shape(data)
#c1_vector =  data[:,0,0,0]
#c2_vector = data[0,:,0,1]
#freq_vector =  data[0,0,:,2]

#print 'c1 scan was ', c1_vector 
#print 'c2 scan was ', c2_vector
#print 'frequency scan was ', freq_vector

#for i in range(steps_c1):
	#plt.figure(i)
	#for j in range(steps_c2):
		#print (c1_vector[i],c2_vector[j])
		##plt.plot(freq_vector,data[i,j,:,5],color = str(1-float(j)/21) ,label = str(c2_vector[j]))
		#plt.plot(freq_vector,data[i,j,:,5],label = str(c2_vector[j]))
	#plt.legend(loc= 3)
	#plt.show()
	#raw_input('press enter')
	
##for i in range(steps_c2):
	#plt.figure(i)
	#for j in range(steps_c1):
		#print (c2_vector[i],c1_vector[j])
		#plt.plot(freq_vector,data[i,j,:,5],color = rainbowlistred[j] ,label = str(c1_vector[j]))
	#plt.legend(loc= 3)
	#plt.show()
	#raw_input('press enter')