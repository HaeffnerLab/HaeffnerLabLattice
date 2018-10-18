import  labrad
import numpy as np
import matplotlib.pyplot as plt
from labrad.units import WithUnit as U
from scipy.optimize import curve_fit
 

cxn = labrad.connect()
sc = cxn.scriptscanner
dv = cxn.data_vault

# 
def get_data(ds):
    direc, dset = ds[0]
    dv.cd(direc)
    dv.open(dset)
    return dv.get()

def get_directory(ds):
    return '/'.join(ds[0][0])[1:]

# fit function to a sin 
def my_sin(x,  amplitude, phase, offset):
    return 1.0*amplitude*np.sin(0.5*x*np.pi/180.0 + phase)**2.0  + offset




# modify new_sequence to take a list of override parameters

scan = [('RamseyGlobalEchoPowerSpectralDensity', ('Ramsey.second_pulse_phase', 0., 720.0, 18.0, 'deg'))]
#'Ramsey.second_pulse_phase': [(0, 360., 15, 'deg') ,'ramsey'

tau_list=[250, 800, 6000, 0]
n_list=[1,3,5,7,9,11] #list(range(1, 19))

for tau in tau_list:

    print "Using Ramsey duration:", tau
    contrast=np.zeros_like(n_list, dtype=float)
    for i,n in enumerate(n_list):
        print "Setting N=", n
        sc.set_parameter('RamseyScanGap','ramsey_duration',U(1.0*tau,'us'))
        sc.set_parameter('RamseyScanGap','dynamical_decoupling_num_pulses', float(n))
        ident = sc.new_sequence('RamseyGlobalEchoPowerSpectralDensity', scan)
        print "scheduled the sequence"
        sc.sequence_completed(ident) # wait until sequence is completed

        ds = sc.get_dataset(ident) # needs to be implemented
        data = np.array(get_data(ds))
        x = data[:,0] 
        prob = data[:,1]
        p0=[1.0,0.0,0.0]
        fit=curve_fit(my_sin,x,prob,p0=p0)
        print "fit params",fit[0]
        print "finished scanning tau=",tau, "N=", n
        print "amplitude is",fit[0][0]
        contrast[i]=fit[0][0]
        
        #np.savetxt('Ramsey_PSD.csv', (get_directory(ds),tau,n,contrast), delimiter=',')
        csv_row = ','.join([get_directory(ds), str(tau), str(n), str(fit[0][0])])
        with open('Ramsey_PSD_deltam2_001.csv','a') as fd:
            fd.write(csv_row)
            fd.write('\n')
        #plt.plot(x, prob,'ro',label='data')
        #plt.plot(np.arange(0.0,360.0,1.0),my_sin(np.arange(0.0,360.0,1.0),*fit[0]),label='fit')
        #plt.legend()
        #plt.show()

cxn.disconnect()

#plt.plot(ts,contrast,'r',label='fring contrast')
#plt.xlabel('wait_time [us]')
#plt.ylabel('fring contrast')
#plt.show()