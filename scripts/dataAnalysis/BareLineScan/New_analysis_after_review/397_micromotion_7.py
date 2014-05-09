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
    B = params['B'].value*1.40
    gamma=params['gamma'].value
    amplitude=params['amplitude'].value
    offset=params['offset'].value
    center=params['center'].value
    x = x-center
    flour = np.zeros_like(x)
    
    for n in np.arange(-5,5,1):
        flour_temp1 = bessel.jv(n,beta)**2/((x+n*Omega-4.0*B/3.0)**2+(gamma/2.0)**2)  ### sigma CG = sqrt(2/3)
        flour_temp2 = 0.0*bessel.jv(n,beta)**2/((x+n*Omega-2.0*B/3.0)**2+(gamma/2.0)**2)  ### pi CG = sqrt(1/3)
        flour_temp3 = bessel.jv(n,beta)**2/((x+n*Omega+4.0*B/3.0)**2+(gamma/2.0)**2)  ### sigma
        flour_temp4 = 0.0*bessel.jv(n,beta)**2/((x+n*Omega+2.0*B/3.0)**2+(gamma/2.0)**2)  ### pi
        flour = flour+amplitude*(flour_temp1+flour_temp2+flour_temp3+flour_temp4)/4.0
    flour=flour+offset
    return flour
'''
define how to compare data to the function
'''
def micro_fit(params , x, data, err):
    model = micro_model(params, x)
    return (model - data)/err


cxn = labrad.connect('192.168.169.197')
dv = cxn.data_vault
dv.cd('','Experiments','BareLineScan','2013Dec21','1506_01')
dv.open(3)
data1=dv.get().asarray

data1_x = data1[:,0]
data1_yerr = np.sqrt(data1[:,1])
data1_y = data1[:,1]

data1_y = data1_y[:-3]
data1_yerr = data1_yerr[:-3]
data1_x = data1_x[:-3]

dv.cd('','Experiments','BareLineScan','2013Dec21','1514_36')
# dv.cd('','Experiments','BareLineScan','2013Dec21','1525_04')
# dv.cd('','Experiments','BareLineScan','2013Dec21','1545_50')
# dv.cd('','Experiments','BareLineScan','2013Dec21','1553_20')
# dv.cd('','Experiments','BareLineScan','2013Dec21','1600_21')
# dv.cd('','Experiments','BareLineScan','2013Dec21','1608_05')
# dv.cd('','Experiments','BareLineScan','2013Dec21','1615_13')
# dv.cd('','Experiments','BareLineScan','2013Dec21','1918_37')
dv.open(3)
data2=dv.get().asarray

data2_y = data2[:,1]
data2_yerr = np.sqrt(data2[:,1])
data2_x = data2[:,0]+38.6

data2_y = data2_y[:]
data2_yerr = data2_yerr[:]
data2_x = data2_x[:]

# data_x = np.concatenate((data1_x,data2_x),axis=0)*2.0
# data_y = np.concatenate((data1_y,data2_y),axis=0)
# data_yerr = np.concatenate((data1_yerr,data2_yerr),axis=0)

data_x = data2_x*2.0
data_y = data2_y
data_yerr = data2_yerr

#data_x = data2_x
#data_y = data2_y
#data_yerr = data2_yerr
#data_y = data_y/(1+0.015*data_y/7300)
#y_err = np.sqrt(data_y)*1.02
y_err = data_y*0.04*0.06+np.sqrt(data_y)

#pyplot.plot(data1_x,data1_y)
#pyplot.plot(data2_x,data2_y)
#pyplot.plot(data_x,data_y)


params = lmfit.Parameters()
params.add('amplitude', value = 1134530, min = 0)
#params.add('gamma', value = 30.7)
params.add('offset', value = 300)
params.add('beta', value = 1.21, vary=True)
#params.add('Omega', value = 24.4)
params.add('B', value = 1.4*0.8,vary=True)
params.add('center', value = 227)

params.add('gamma', value = 24.8,vary = True)
params.add('Omega', value = 30.704, vary = True)

result = lmfit.minimize(micro_fit, params, args = (data_x, data_y, y_err))

fit_values  = data_y + result.residual

print result.redchi

lmfit.report_errors(params)
    
pyplot.plot(np.arange(120,340,0.1)-params['center'],(micro_model(params,np.arange(120,340,0.1))-300)/7, linewidth=1.5)
pyplot.errorbar(data_x-params['center'],(data_y-300)/7,data_yerr/7,linestyle='None',markersize = 4.0,fmt='o',color='black')
#pyplot.plot(data_x-params['center'],result.residual)
pyplot.xlim([-110,110])

pyplot.show()