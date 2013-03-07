import labrad
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot, pylab
from scipy.special.orthogonal import eval_genlaguerre as laguer
import numpy as np
from scipy import optimize
#from scipy.stats import chi2
import TheoryPrediction as tp
import timeevolution as te

class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value
        
def fit(function, parameters, y, x = None):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = np.arange(y.shape[0])
    p = [param() for param in parameters]
    return optimize.leastsq(f, p)

#get access to servers
cxn = labrad.connect('192.168.169.197', password = 'lab')
dv = cxn.data_vault

# set to right date
date = '2013Mar05'

#provide list of Rabi flops - all need to have same x-axis
flop_directory = ['','Experiments','RabiFlopping',date]
flop_files = ['1804_40','1814_58','1820_08','1749_12','1759_31','1825_37','1809_49','1830_47','1754_21','1835_56']

#provide list of evolutions with different phases - all need to have same x-axis
dephase_directory = ['','Experiments','RamseyDephaseScanSecondPulse',date]
dephase_files = ['1812_24','1751_46','1822_42','1802_05','1833_21','1756_56','1807_14','1828_12','1817_33']

flop_numbers = range(len(flop_files))
dephase_numbers = range(len(dephase_files))

#Time when dephasing is implemented (usually half of Rabi pi time)
dephasing_time = 27.73e-6
sideband = 1
trap_frequency = 2.8e6
amax=1000
nb = Parameter(1.4)
omega = Parameter(200898.55038)
delta = Parameter(100.0)

# take list of Rabi flops and average
dv.cd(flop_directory)
flop_y_axis_list=[]
for i in flop_numbers:
    dv.cd(flop_files[i])
    dv.open(1)
    data = dv.get().asarray
    flop_y_axis_list.append(data[:,1])
    dv.cd(1)

flop_y_axis = np.sum(flop_y_axis_list,axis=0)/np.float32(len(flop_files))
flop_x_axis=data[:,0]*10**(-6)

xmax=max(flop_x_axis)

# take list of evolutions with differnet phases and average --> dephasing!
dv.cd(dephase_directory)
deph_y_axis_list=[]
for i in dephase_numbers:
    dv.cd(dephase_files[i])
    dv.open(1)
    data = dv.get().asarray
    deph_y_axis_list.append(data[:,1])
    dv.cd(1)

deph_y_axis = np.sum(deph_y_axis_list,axis=0)/np.float32(len(dephase_files))
deph_x_axis=(data[:,0]+dephasing_time)*10**(-6)

#fit to theory

evo=te.StateEvolution(amax)
def f(x): 
    evolution = evo.rabiflop(nb(),omega(),delta(),sideband,x)
    return evolution

fitting_region = np.where((flop_x_axis >= 0.000000)&(flop_x_axis <= 0.00025))
p,success = fit(f, [nb,omega,delta], y = flop_y_axis[fitting_region], x = flop_x_axis[fitting_region])

figure = pyplot.figure()

print "nbar = ",nb()
print "Rabi Frequency (Driving strength) = ", omega()*10**(-3)/(2.*np.pi)," kHz"
print "Detuning = {}".format(delta())

# this calls tp to make the plots by the functions defined in TheoryPrediction.py (takes times in units of rabi frequency (driving strength)
sb=tp.Sideband(nb(), sideband=sideband,omega=omega(),nu=2.*np.pi*trap_frequency)
t0=dephasing_time
sb.anaplot(0, xmax*sb.p.omega/(2.*np.pi), 100, t0*sb.p.omega/(2.*np.pi), dephasing=True, discord=False, lsig=True)
m=pylab.unravel_index(np.array(sb.flop).argmax(), np.array(sb.flop).shape)
print 'Flop maximum at {:.2f} us'.format(sb.x[m]*2.*np.pi/sb.p.omega)+' -> Expected optimal t0 at {:.2f} us'.format(sb.x[m]*2.*np.pi/sb.p.omega/2.)
# rescale x-axis
sb.x=2.*np.pi*sb.x/sb.p.omega
pyplot.plot(sb.x*10**6,evo.rabiflop(nb(),omega(),delta(),sideband,sb.x))
pyplot.plot(sb.x*10**6,sb.deph)
#pyplot(sb.x,sb.flop)

pyplot.plot(flop_x_axis*10**6,flop_y_axis, '-o')
pyplot.plot(deph_x_axis*10**6,deph_y_axis, '-o')
pyplot.xlabel('t in us')
pyplot.ylim((0,1))
pyplot.ylabel('Population in the D-5/2 state')# + {0:.0f} kHz'.format(ymin))
#pyplot.legend()
pyplot.text(xmax*0.70*10**6,0.83, 'nbar = {:.2f}'.format(nb()))
pyplot.text(xmax*0.70*10**6,0.88, 'Rabi Frequency f = {:.2f} kHz'.format(omega()*10**(-3)/(2.*np.pi)))
pyplot.title('Local detection on the first blue sideband')
pyplot.show()
