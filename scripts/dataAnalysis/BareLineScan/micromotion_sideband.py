from __future__ import division
import numpy as np
from matplotlib import pyplot
from scipy import linalg
from scipy import special as bessel
import labrad

#cxn = labrad.connect('192.168.169.49')
#dv = cxn.datavault
#dv.cd('','Experiments','BareLine')

Omega = 1.3
beta_array = np.array([0.8])#np.linspace(1.7,2.3,6) # np.linspace(0,2,3)
Delta = np.linspace(-5.0,5.0,500)
B_array = np.array([0.0]) ## magnetic field

for B in B_array:
	for beta in beta_array:
		flour = np.zeros_like(Delta)
		for n in np.arange(-50,51,1):
			flour_temp1 = bessel.jv(n,beta)**2/((Delta+n*Omega-4.0*B/3.0)**2+(0.5)**2)
			flour_temp2 = bessel.jv(n,beta)**2/((Delta+n*Omega-2.0*B/3.0)**2+(0.5)**2)
			flour_temp3 = bessel.jv(n,beta)**2/((Delta+n*Omega+4.0*B/3.0)**2+(0.5)**2)
			flour_temp4 = bessel.jv(n,beta)**2/((Delta+n*Omega+2.0*B/3.0)**2+(0.5)**2)
			flour = flour+(flour_temp1+flour_temp2+flour_temp3+flour_temp4)/4.0
		pyplot.plot(Delta,flour)
	
pyplot.show()