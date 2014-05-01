from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit
import datetime

def cosine_model(params, x):
    freq = 1/(sidereal_day*3600) ## this is omega t
    A = params['A'].value
    B = params['B'].value
    C = params['C'].value
    D = params['D'].value
    offset = -0.008176
    
    '''
    change parameter basis
    '''
    p = np.array([0.0,0.0,0.0,0.0])
    eigen_vec = np.array([[ 0.73574237,  0.5958259 , -0.32107059,  0.02425566],
       [ 0.40385994, -0.7470089 , -0.43858181,  0.29414426],
       [-0.54294475,  0.25905347, -0.74087101,  0.29868452],
       [ 0.02813036,  0.14092726,  0.39455015,  0.90756728]])
    p[0] =eigen_vec[0,0]*A+eigen_vec[0,1]*B+eigen_vec[0,2]*C+eigen_vec[0,3]*D
    p[1] =eigen_vec[1,0]*A+eigen_vec[1,1]*B+eigen_vec[1,2]*C+eigen_vec[1,3]*D
    p[2] =eigen_vec[2,0]*A+eigen_vec[2,1]*B+eigen_vec[2,2]*C+eigen_vec[2,3]*D
    p[3] =eigen_vec[3,0]*A+eigen_vec[3,1]*B+eigen_vec[3,2]*C+eigen_vec[3,3]*D
    output = p[0]*np.cos(2*np.pi*x*freq)+p[1]*np.sin(2*np.pi*x*freq)+p[2]*np.cos(2*np.pi*x*2*freq)+p[3]*np.sin(2*np.pi*x*2*freq)+offset

    #offset=params['offset'].value
    #output = A*np.cos(2*np.pi*x*freq)+B*np.sin(2*np.pi*x*freq)+C*np.cos(2*np.pi*x*2*freq)+D*np.sin(2*np.pi*x*2*freq)-0.008176
#     output = A*np.cos(2*np.pi*x*freq)+B*np.sin(2*np.pi*x*freq)+C*np.cos(2*np.pi*x*2*freq)+D*np.sin(2*np.pi*x*2*freq)+offset
    

    return output
'''
define how to compare data to the function
'''
def cosine_fit(params , x, data, err):
    model = cosine_model(params, x)
    return (model - data)/err

'''
Analyse the whole data set to see how gaussian the noise is
'''

def gaussian_model(params, x):
    A = params['A'].value
    width = params['width'].value
    center=params['center'].value
    output = A*np.exp(-0.5*(x-center)**2/(width**2))
    return output
'''
define how to compare data to the function
'''
def gaussian_fit(params , x, data, err):
    model = gaussian_model(params, x)
    return (model - data)/err

# cxn = labrad.connect()
# dv = cxn.data_vault

####### common variable ######

ramsey_time = 0.095
Berkeley_longitude = 122.2728/360
sidereal_day = 23.9344699 ### in hours
### UTC is faster than Berkeley time
offset_from_UTC = Berkeley_longitude*sidereal_day*60*60
equinox = datetime.datetime(2014, 3, 20, 16, 57, 6)
## which phase?
dataset = 9

b_field_correction = True
axial_correction = True
binner = True


######################## DAY 1 start ##############    

# dv.cd(['','Drift_Tracking','LLI_tracking_all_data','2014Apr18'])
# dv.open(1)
# data = dv.get().asarray
# 
# np.save('dataApr18.npy',data)

data = np.load('dataApr18.npy')

time = data[:,0]

#where_early = np.where(((time>74000)&(time<84878))|(time>85709))
where_early = np.where(time>74000)
where_late = np.where(time<32476)
time = np.append(time[where_early],time[where_late]+86400)

### time conversion ####
# data starts on April 13, 2014, 69297.0 Berkeley time
### UTC is faster than Berkeley time
### add offset to data
time = time + offset_from_UTC - 86400 ## Now becomes seconds since April 19 UTC time
# April 13, 2014 at midnight Berkeley is 
# 2014 equinox is March 20 16:57:06 UTC, which is 
experiment_day = datetime.datetime(2014, 4, 19, 00, 00, 00)
time_difference = experiment_day - equinox
### convert time to seconds since equinox
time = time + time_difference.total_seconds()
#### end of time conversion ####

### get phase data and correction from axial trap and B-field ###

phase = data[:,dataset]-np.average(data[:,dataset]) #3,7,9

phase = np.append(phase[where_early],phase[where_late])
b_field = data[:,10]
axial = data[:,12]
b_field = np.append(b_field[where_early],b_field[where_late])
axial = np.append(axial[where_early],axial[where_late])
 
axial = (axial-np.average(axial))*1000*0.027*ramsey_time*360 ## convert to phase correction 27 mHz per kHz
b_field = ((b_field-np.average(b_field))*2*8/np.average(b_field))*ramsey_time*360 ## convert to phase correction 8 Hz at 3.9 gauss
 
#### apply correction due to B-field and axial trap frequency ####

if axial_correction:
    #axial[np.where(axial<-0.7)] = np.ones_like(axial[np.where(axial<-0.7)])*np.average(axial)
    phase = phase - axial
if b_field_correction:
    phase = phase - b_field
    
x1 = time
axial1 = axial/360/ramsey_time
b1 = b_field/360/ramsey_time
y1 = phase/360/ramsey_time
    
######################## DAY 1 end ##############    

######################## DAY 2 start ##############    

# dv.cd(['','Drift_Tracking','LLI_tracking_all_data','2014Apr19'])
# dv.open(1)
# data = dv.get().asarray
# np.save('dataApr19.npy',data)
data = np.load('dataApr19.npy')
time = data[:,0]

#where_early = np.where(time>34000)
where_early = np.where((time>41000)|((time<39000)&(time>34000)))  ### exclude where laser fell out
where_late = np.where(time<20000)
time = np.append(time[where_early],time[where_late]+86400)

### time conversion ####
# data starts on April 13, 2014, 69297.0 Berkeley time

### add offset to data
time = time + offset_from_UTC - 86400 ## Now becomes seconds since April 19 UTC time
# April 13, 2014 at midnight Berkeley is 
# 2014 equinox is March 20 16:57:06 UTC, which is 
experiment_day = datetime.datetime(2014, 4, 20, 00, 00, 00)
time_difference = experiment_day - equinox
### convert time to seconds since equinox
time = time + time_difference.total_seconds()
#### end of time conversion ####

### get phase data and correction from axial trap and B-field ###
phase = data[:,dataset]-np.average(data[:,dataset]) #3,7,9

phase = np.append(phase[where_early],phase[where_late])
b_field = data[:,10]
axial = data[:,12]
b_field = np.append(b_field[where_early],b_field[where_late])
axial = np.append(axial[where_early],axial[where_late])
 
axial = (axial-np.average(axial))*1000*0.027*ramsey_time*360 ## convert to phase correction 27 mHz per kHz
b_field = ((b_field-np.average(b_field))*2*8/np.average(b_field))*ramsey_time*360 ## convert to phase correction 8 Hz at 3.9 gauss
 
#### apply correction due to B-field and axial trap frequency ####
 
if axial_correction:
    #axial[np.where(axial<-0.7)] = np.ones_like(axial[np.where(axial<-0.7)])*np.average(axial)
    phase = phase - axial
if b_field_correction:
    phase = phase - b_field
    
x2 = time
axial2 = axial/360/ramsey_time
b2 = b_field/360/ramsey_time
y2 = phase/360/ramsey_time
    
######################## DAY 2 end ##############  


### add 2 days of data together ###

x = np.append(x1,x2)
y = np.append(y1,y2)
#y = np.append(axial1,axial2)
#y = np.append(b1,b2)

data_length = (x[-1]-x[0])/3600

print "Data length = ",data_length

np.save('2014_04_18_weekend_freq.npy',y)
np.savetxt('LLI_final_data.csv',np.transpose(np.array([x-x[0],y])),delimiter=',')
np.save('2014_04_18_weekend_time.npy',x)

## assume quantum projection noise
yerr = np.sqrt(np.arcsin(1/np.sqrt(4*100)/0.50)**2+np.arcsin(1/np.sqrt(4*100)/0.35)**2)/(2*np.pi*ramsey_time)
print "Quantum projection noise = ", yerr, " Hz"


#### binner ####



if binner:
    freq = y
    time = x
    time_offset = x[0]
    x = x-time_offset
    time = time-time_offset
    time_chunk = 3600
    #bin_size = 5000
    offset = 3600
    #number_of_bin = int(np.max(time)/bin_size)-1
    number_of_chunk = int(np.max(time)/time_chunk)
    
    freq_binned = []
    freq_sd_array = []
    time_binned = []
    
    for i in range(0,int(number_of_chunk*time_chunk/offset)):
        #print i
        where = np.where((time>(i*offset))*(time<(i*offset+time_chunk)))
        if np.size(freq[where])<2:
            continue
        freq_mean = np.average(freq[where])
        #print "points per bin = ", np.size(freq[where])
        freq_sd = np.std(freq[where])/np.sqrt(np.size(freq[where])-1)
        #print freq_sd
        freq_binned.append(freq_mean)
        freq_sd_array.append(freq_sd)
        
        
        time_stamp = (i+0.5)*offset
        time_binned.append(time_stamp)
        #time_binned.append((i+1)*bin_size)
    
    x = time_binned + time_offset
    y = freq_binned
    yerr = freq_sd_array

print "average sd is ", np.average(yerr)
################

params = lmfit.Parameters()

params.add('A', value = 0, vary = True) ##cos ### -3 cXZ sin 2 chi: 7 +- 23 mHz
params.add('B', value = 0, vary = True) ##sin ### -3 cYZ sin 2 chi: 32 +- 56 mHz
params.add('C', value = 0, vary = True) ##cos2 ### -1.5 (cXX-cYY) sin^2 chi: 15 +- 22 mHz
params.add('D', value = 0, vary = True) ##sin2 ### -3 cXY sin^2 chi: 8 +- 20 mHz
#params.add('offset', value = 0.0)

result = lmfit.minimize(cosine_fit, params, args = (x, y, yerr))

residual_array = result.residual*yerr

#fit_values  = y + result.residual

lmfit.report_errors(params, min_correl=0)

print "Reduced chi-squared = ", result.redchi

#ci = lmfit.conf_interval(result)
# print "A correlations = ", params['A'].correl
# print "B correlations = ", params['B'].correl
# print "C correlations = ", params['C'].correl
# print "D correlations = ", params['D'].correl

#### construct correlation matrix

correl_matrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])*1.0
variable_array = ['A','B','C','D']
for i in range(0,4):
    for j in range(0,4):
        if i != j:
            value = params[variable_array[i]].correl[variable_array[j]]*params[variable_array[i]].stderr*params[variable_array[j]].stderr
            correl_matrix[i,j] = value
        else:
            value = params[variable_array[i]].stderr*params[variable_array[j]].stderr
            correl_matrix[i,j] = value            

print "Covariance matrix is = ", correl_matrix
print "Eigenvalues of (sqrt) cov matrix is =", np.sqrt(np.linalg.eig(correl_matrix)[0])
print "Eigenvectors of cov matrix is =", np.linalg.eig(correl_matrix)

for i in range(0,4):
    for j in range(0,4):
        value = correl_matrix[i,j]/(params[variable_array[i]].stderr*params[variable_array[j]].stderr)
        correl_matrix[i,j] = value
print "Correl matrix is = ", correl_matrix


# report confidence interval
#lmfit.report_ci(ci)
x = x-x[0]
x_plot = np.linspace(x.min()-1000,x.max()+1000,1000)

### plot phase data and fit model ###
figure = pyplot.figure(1)
figure.clf()
pyplot.plot(x,y,'o')
pyplot.plot(x_plot,cosine_model(params,x_plot),linewidth = 3.0)
if binner:
    pyplot.errorbar(x,y,yerr*np.sqrt(result.redchi),fmt='o')

### plot residual histogram and fit to gaussian

residual_histogram = np.histogram(residual_array,bins=100,range=(-0.5,0.5))
x = residual_histogram[1][:-1]
y = residual_histogram[0]
##
yerr = np.sqrt(residual_histogram[0])

yerr[np.where(yerr<=0.0)] = np.ones_like(yerr[np.where(yerr<=0.0)])

params = lmfit.Parameters()
 
params.add('A', value = 140)
params.add('width', value = 0.2)
params.add('center', value = 0.0)


figure = pyplot.figure(2)
figure.clf()
result = lmfit.minimize(gaussian_fit, params, args = (x, y, yerr))
 
fit_values  = y + result.residual
print "--------- Gaussian fit -----------------"
lmfit.report_errors(params)
 
print "Reduced chi-squared Gaussian = ", result.redchi

x_plot = np.linspace(x.min(),x.max(),1000)

pyplot.errorbar(x,y,yerr, linestyle='None',markersize = 4.0,fmt='o',color='black')
pyplot.plot(x_plot,gaussian_model(params,x_plot),linewidth = 3.0)
pyplot.show()