import labrad
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chi2
import TheoryPrediction as tp
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

# set to right date
date = '2013Feb05'

flop_directory = ['','Experiments','729Experiments','RabiFlopping',date]
dephase_directory = ['','Experiments','729Experiments','RamseyDephase',date]
# rabi flop evolution without dephasing
rabiflop_dir = '1433_43'#actually '1538_01' in 'RamseyDephase' but this one starts at dephasing time instead of zero
rabiflop_filename = '00001 - Rabi Flopping {0}_{1}'.format(date,rabiflop_dir)

#provide list of evolutions with different phases - all need to have same x-axis
dephased_dirs = ['1538_32','1540_32','1541_12','1538_52','1540_52','1539_12','1539_52','1541_32','1540_12','1539_32']
dephased_number = range(len(dephased_dirs))

#Time when dephasing is implemented (usually half of Rabi pi time)
dephasing_time = 0.000025

dv.cd(flop_directory)
dv.cd(rabiflop_dir)
dv.open(rabiflop_filename)
data = dv.get().asarray
flop_x_axis = data[:,0]
flop_y_axis = data[:,1]

dv.cd(dephase_directory)
deph_y_axis_list=[]
for i in dephased_number:
    dv.cd(dephased_dirs[i])
    dv.open('00001 - Ramsey Dephase {0}_{1}'.format(date,dephased_dirs[i]))
    data = dv.get().asarray
    deph_y_axis_list.append(data[:,1])
    dv.cd(1)

deph_y_axis = np.sum(deph_y_axis_list,axis=0)/np.float32(len(dephased_dirs))
deph_x_axis=data[:,0]+dephasing_time

xmax = max(flop_x_axis)

figure = pyplot.figure()

#fit to a line
#
#p0 = [-0.25, 0.2] # initial values of parameters
#f = lambda x, m, b: b + m*x # define the function to be fitted
#
#p, covm = curve_fit(f, x_axis, y_axis, p0) # do the fit
#m,b = p

sb=tp.Sideband(4.71020123757, -1,omega=1491898.55038/2.,nu=2.8*2.*np.pi*1000000.)
tmax=xmax*sb.p.omega/(2.*np.pi)
print sb.p.eta
sb.anaplot(0, tmax, 100, 2.5, dephasing=True, discord=False, lsig=True)
# rescale x-axis
sb.x=2.*np.pi*sb.x/sb.p.omega
pyplot.plot(sb.x*10**6,sb.flop)
pyplot.plot(sb.x*10**6,sb.deph)
#pyplot(sb.x,sb.flop)

pyplot.plot(flop_x_axis*10**6,flop_y_axis, '-o')
pyplot.plot(deph_x_axis*10**6,deph_y_axis, '-o')
#pyplot.plot(x_axis, f(x_axis, m, b), 'r', label = 'Slope of {0:.1f} KHz / min'.format(abs(m)))
pyplot.xlabel('t in microseconds')
pyplot.ylabel('Population in the D-5/2 state')# + {0:.0f} kHz'.format(ymin))
#pyplot.legend()
pyplot.title('Local detection on the first red sideband')
pyplot.show()
