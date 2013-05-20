import labrad
import matplotlib

from matplotlib import pyplot, pylab
from scipy.special.orthogonal import eval_genlaguerre as laguer
import numpy as np
from scipy import optimize
#from scipy.stats import chi2
import TheoryPrediction as tp

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
date = '2013Feb05'

#provide list of Rabi flops - all need to have same x-axis
flop_directory = ['','Experiments','729Experiments','RabiFlopping',date]
flop_files = ['1433_43','1431_49','1435_40']

#provide list of evolutions with different phases - all need to have same x-axis
dephase_directory = ['','Experiments','729Experiments','RamseyDephase',date]
dephase_files = ['1538_32','1540_32','1541_12','1538_52','1540_52','1539_12','1539_52','1541_32','1540_12','1539_32']


flop_numbers = range(len(flop_files))
dephase_numbers = range(len(dephase_files))

#Time when dephasing is implemented (usually half of Rabi pi time)
dephasing_time = 25e-6
sideband = -1
trap_frequency = 2.8e6
amax=1000

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
flop_x_axis=data[:,0]

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
deph_x_axis=data[:,0]+dephasing_time

#fit to theory
nb = Parameter(10)
omega = Parameter(1491898.55038)

class StateEvolution:
    def __init__(self,nmax):
        hbar=1.054571726*10**(-34)
        m=1.660538921*40*10**(-27)
        self.eta = 2.*np.cos(np.pi/4)*np.pi/729*10**9*np.sqrt(hbar/(2.*m*2.*np.pi*trap_frequency))
        self.n=np.linspace(0,nmax,nmax+1)
        
    def omegaeff(self,omega0,sideband_order,n):#diverges for n -> infinity
        sideband_order=np.abs(sideband_order)
        x=1
        for k in np.linspace(1,sideband_order,sideband_order):
            x=x*(n+k)
        result = self.eta**sideband_order*omega0/2.*np.exp(-self.eta**2./2.)*laguer(n,sideband_order,self.eta**2.)/np.sqrt(x)
        return result
        
    def pnb(self,nbar,sideband_order,n):#thermal state
        nplus=0.
        if sideband_order<0:
            nplus=-np.float32(sideband_order)
        result=(nbar/(nbar+1.))**(n+nplus)/(nbar+1.)
        return result

    def rabiflop(self,nbar,omega0,sideband_order,t):
        n=self.n
        result=np.sum(self.pnb(nbar,sideband_order,np.outer(n,np.ones_like(t)))*np.sin(np.outer(self.omegaeff(omega0,sideband_order,n),t))**2,axis=0)
        return result

evo=StateEvolution(amax)
def f(x): 
    evolution = evo.rabiflop(nb(),omega(),sideband,x)
    return evolution

fitting_region = np.where(flop_x_axis <= xmax)
p,success = fit(f, [nb,omega], y = flop_y_axis[fitting_region], x = flop_x_axis[fitting_region])

figure = pyplot.figure()

print "nbar = ",nb()
print "Rabi Frequency (Driving strength) = ", omega()*10**(-3)/(2.*np.pi)," kHz"

# this calls tp to make the plots by the functions defined in TheoryPrediction.py (takes times in units of rabi frequency (driving strength)
sb=tp.Sideband(nb(), sideband=sideband,omega=omega(),nu=2.*np.pi*trap_frequency)
t0=dephasing_time
sb.anaplot(0, xmax*sb.p.omega/(2.*np.pi), 100, t0*sb.p.omega/(2.*np.pi), dephasing=True, discord=False, lsig=True)
m=pylab.unravel_index(np.array(sb.flop).argmax(), np.array(sb.flop).shape)
print 'Flop maximum at {:.2f} us'.format(sb.x[m]*10**6*2.*np.pi/sb.p.omega)+' -> Expected optimal t0 at {:.2f} us'.format(sb.x[m]*10**6*2.*np.pi/sb.p.omega/2.)
# rescale x-axis
sb.x=2.*np.pi*sb.x/sb.p.omega
pyplot.plot(sb.x*10**6,sb.flop)
pyplot.plot(sb.x*10**6,sb.deph)
#pyplot(sb.x,sb.flop)

pyplot.plot(flop_x_axis*10**6,flop_y_axis, '-o')
pyplot.plot(deph_x_axis*10**6,deph_y_axis, '-o')
pyplot.xlabel('t in us')
pyplot.ylim((0,1))
pyplot.ylabel('Population in the D-5/2 state')# + {0:.0f} kHz'.format(ymin))
#pyplot.legend()
pyplot.text(xmax*0.50*10**6,0.73, 'nbar = {:.2f}'.format(nb()))
pyplot.text(xmax*0.50*10**6,0.78, 'Rabi Frequency f = {:.2f} kHz'.format(omega()*10**(-3)/(2.*np.pi)))
pyplot.title('Local detection on the first red sideband')
pyplot.show()
