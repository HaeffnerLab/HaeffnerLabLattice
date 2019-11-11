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

# fit function to a sin 
def my_sin(x,  amplitude, phase, offset):
    return 1.0*amplitude*np.sin(0.5*x*np.pi/180.0 + phase)**2.0  + offset




# modify new_sequence to take a list of override parameters

scan = [('RamseyLocalHanEcho',   ('Ramsey.second_pulse_phase', 0., 360.0, 30.0, 'deg'))]
#'Ramsey.second_pulse_phase': [(0, 360., 15, 'deg') ,'ramsey'

ts=np.arange(100.0,10000.0,200.0)

print ts

contrast=np.zeros_like(ts)
for i,t in enumerate(ts):
    print "Scanning time" , t
    sc.set_parameter('RamseyScanGap','ramsey_duration',U(1.0*t,'us'))
    ident = sc.new_sequence('RamseyLocalHanEcho', scan)
    print "scheduled the sequence"
    sc.sequence_completed(ident) # wait until sequence is completed

    ds = sc.get_dataset(ident) # needs to be implemented
    data = np.array(get_data(ds))
    x = data[:,0] 
    prob = data[:,1]
    p0=[1.0,0.0,0.0]
    fit=curve_fit(my_sin,x,prob,p0=p0)
    print "fit params",fit[0]
    print "finished scanning time " , t
    print "amplitude is",fit[0][0]
    contrast[i]=fit[0][0]
    
    np.savetxt('HanEcho.csv', (ts,contrast),  delimiter=',')
    #plt.plot(x, prob,'ro',label='data')
    #plt.plot(np.arange(0.0,360.0,1.0),my_sin(np.arange(0.0,360.0,1.0),*fit[0]),label='fit')
    #plt.legend()
    #plt.show()

cxn.disconnect()

plt.plot(ts,contrast,'r',label='fring contrast')
plt.xlabel('wait_time [us]')
plt.ylabel('fring contrast')
plt.show()