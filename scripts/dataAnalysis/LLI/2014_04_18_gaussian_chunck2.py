from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit


def gaussian_model(params, x):
    A = params['A'].value
    width = params['width'].value
    center=params['center'].value
    output = A*np.exp(-(x-center)**2/(2*width**2))
    return output
'''
define how to compare data to the function
'''
def gaussian_fit(params , x, data, err):
    model = gaussian_model(params, x)
    return (model - data)/err

def cosine_model(params, x):
    sidereal_day = 23.9344699
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



#data = np.load('2014_04_13_all_data.npy')
time = np.load('2014_04_18_weekend_time.npy')
time = time-time[0]
freq = np.load('2014_04_18_weekend_freq.npy')

figure = pyplot.figure(1)
for k in [100,200,500,1000]:
    time_chunk = k
    number_of_chunk = int(np.max(time)/time_chunk)
    print number_of_chunk
    offset = 100
    width_array = []
    freq_array = []
    time_array = []
    
    for i in range(0,int(number_of_chunk*time_chunk/offset)):  
        where = np.where((time>(i*offset))*(time<(i*offset+time_chunk)))
        time_stamp = (i+0.5)*offset
        
        freq_slice = freq[where]
        if np.size(freq_slice) < 2.0:
            continue
        time_array.append(time_stamp)
        freq_array.append(np.average(freq_slice))
        
        freq_diff = freq_slice - np.average(freq_slice)
        freq_histogram = np.histogram(freq_diff, 10)
        
        x = freq_histogram[1][:-1]
        y = freq_histogram[0]
        yerr = np.sqrt(freq_histogram[0]+1)
        
    #     params = lmfit.Parameters()
    #      
    #     params.add('A', value = 140)
    #     params.add('width', value = 0.2)
    #     params.add('center', value = 0.0)
    #      
    #     result = lmfit.minimize(gaussian_fit, params, args = (x, y, yerr))
    #      
    #     fit_values  = y + result.residual
    #      
    #     #lmfit.report_errors(params)
        print "number of points =", np.size(freq_slice)
    #     print "width =", params['width'].value, 'Chi = ', result.redchi
        #width_array.append(np.abs(params['width'].value)/np.sqrt(np.size(freq_slice)))
        width_array.append(np.std(freq_slice)/(np.sqrt(np.size(freq_slice)-1)))
        #print 'Chi = ', result.redchi
        
        x_plot = np.linspace(x.min(),x.max(),1000)
        
    #     figure = pyplot.figure(i)
    #     figure.clf()
    #       
    #     pyplot.errorbar(x,y,yerr, linestyle='None',markersize = 4.0,fmt='o',color='black')
    #     pyplot.plot(x_plot,gaussian_model(params,x_plot),linewidth = 3.0)
     
    # width_array = width_array - np.average(width_array)    
    # width_histogram = np.histogram(width_array,20)
    # 
    # x = width_histogram[1][:-1]
    # y = width_histogram[0]
    # yerr = np.sqrt(width_histogram[0]+1)
    # 
    # print x
    # print y
    # 
    # params = lmfit.Parameters()
    #  
    # params.add('A', value = 0.2)
    # params.add('width', value = 0.2)
    # params.add('center', value = 0.0)
    #  
    # result = lmfit.minimize(gaussian_fit, params, args = (x, y, yerr))
    #  
    # fit_values  = y + result.residual
    # 
    # lmfit.report_errors(params)
    # 
    # x_plot = np.linspace(x.min(),x.max(),1000)
    # 
    # pyplot.errorbar(x,y,yerr, linestyle='None',markersize = 4.0,fmt='o',color='black')
    # pyplot.plot(x_plot,gaussian_model(params,x_plot),linewidth = 3.0)
    
    x = np.array(time_array)
    y = np.array(freq_array)
    yerr = np.array(width_array)
    
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
    
    #print result.redchi
    
    #print 1/params['freq'].value/3600
    
    x_plot = np.linspace(x.min(),x.max(),1000)
    
    
    pyplot.plot(x,y,'-')
    #pyplot.plot(x_plot,cosine_model(params,x_plot),linewidth = 3.0)
#pyplot.errorbar(time_array,freq_array,width_array, linestyle='None',markersize = 4.0,fmt='o',color='black')

    
pyplot.show()


'''
bin chunk = 1000: 31(27) mHz
bin chunk = 2000: 43(27) mHz
bin chunk = 4000: 37(49) mHz
bin chunk = 6000: 17(49) mHz
bin chunk = 8000: 51(91) mHz
'''

'''
105(13) mHz, phase = 0.78 --> 5.96 hrs
89(10) mHz, phase = 0.059 --> 5.578 hrs
'''
