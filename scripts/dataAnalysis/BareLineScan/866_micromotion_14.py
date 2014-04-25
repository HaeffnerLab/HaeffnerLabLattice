from __future__ import division
import numpy as np
from matplotlib import pyplot
from scipy import linalg
from scipy import special as bessel
import labrad
import lmfit


def micro_model(params, x):
    beta = params['beta'].value
    Omega= params['Omega'].value
    B = params['B'].value
    gamma=params['gamma'].value
    amplitude=params['amplitude'].value
    offset=params['offset'].value
    center=params['center'].value
    x = x-center
    flour = np.zeros_like(x)
    
    for n in np.arange(-50,51,1):
        flour_temp1 = bessel.jv(n,beta)**2/((x+n*Omega-14.0*B/10.0)**2+(gamma/2.0)**2)
        flour_temp2 = bessel.jv(n,beta)**2/((x+n*Omega-6.0*B/10.0)**2+(gamma/2.0)**2)
        flour_temp3 = bessel.jv(n,beta)**2/((x+n*Omega-2.0*B/10.0)**2+(gamma/2.0)**2)
        flour_temp4 = bessel.jv(n,beta)**2/((x+n*Omega+2.0*B/10.0)**2+(gamma/2.0)**2)
        flour_temp5 = bessel.jv(n,beta)**2/((x+n*Omega+6.0*B/10.0)**2+(gamma/2.0)**2)
        flour_temp6 = bessel.jv(n,beta)**2/((x+n*Omega+14.0*B/10.0)**2+(gamma/2.0)**2)
        flour = flour+amplitude*(flour_temp1+flour_temp2+flour_temp3+flour_temp4+flour_temp5+flour_temp6)/6.0+offset
    return flour
'''
define how to compare data to the function
'''
def micro_fit(params , x, data, err):
    model = micro_model(params, x)
    return (model - data)/err

cxn = labrad.connect()
dv = cxn.data_vault
dv.cd('','Experiments','BareLineScanRed','2013Nov18','1923_14')
dv.open(3)
data1=dv.get().asarray

data1_x = data1[:,0]
data1_yerr = np.sqrt(data1[:,1])/60.0
data1_y = data1[:,1]/60.0

data1_y = data1_y[:-3]
data1_yerr = data1_yerr[:-3]
data1_x = data1_x[:-3]

dv.cd('','Experiments','BareLineScanRed','2013Nov18','1942_13')
dv.open(3)
data2=dv.get().asarray

data2_y = data2[:,1]/50.0
data2_yerr = np.sqrt(data2[:,1])/50.0
data2_x = data2[:,0]+14.5

data2_y = data2_y[6:]
data2_yerr = data2_yerr[6:]
data2_x = data2_x[6:]

data_x = np.concatenate((data1_x,data2_x),axis=0)*2.0
data_y = np.concatenate((data1_y,data2_y),axis=0)
data_yerr = np.concatenate((data1_yerr,data2_yerr),axis=0)

y_err = np.sqrt(data_y)

#pyplot.plot(data1_x,data1_y)
#pyplot.plot(data2_x,data2_y)
#pyplot.plot(data_x-180,data_y)


params = lmfit.Parameters()
params.add('amplitude', value = 2800)
params.add('gamma', value = 24.0, vary = True)
params.add('offset', value = 0.016961)
params.add('beta', value = 1.0)
params.add('Omega', value = 30.704, vary = True)
params.add('B', value = 1.68,min=0)
params.add('center', value = 180)


result = lmfit.minimize(micro_fit, params, args = (data_x, data_y, y_err))

fit_values  = data_y + result.residual

lmfit.report_errors(params)

normalization = params['amplitude']/(params['gamma']/2.0)**2

pyplot.plot(np.arange(110,250,0.1)-params['center'],micro_model(params,np.arange(110,250,0.1))/normalization,linewidth=1.5)
pyplot.errorbar(data_x-params['center'],data_y/normalization,data_yerr/normalization,linestyle='None',markersize = 4.0,fmt='o',color='black')
pyplot.axis([-85,85,0.1,0.8])
#pyplot.plot(np.arange(120,320,0.1)-params['center'],micro_model(params,np.arange(120,320,0.1)))
pyplot.show()