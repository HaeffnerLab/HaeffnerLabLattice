import  labrad
import numpy as np
import matplotlib.pyplot as plt
from labrad.units import WithUnit as U
from scipy.optimize import curve_fit
 

# 
def get_data(dv,ds):
    direc, dset = ds[0]
    dv.cd(direc)
    dv.open(dset)
    return dv.get()


def fit_gaussian(sc,dv,ident):
    # get the data
    ds = sc.get_dataset(ident) # needs to be implemented
    data = np.array(get_data(dv,ds))
    
    f = data[:,0] 
    
    prob = data[:,-1]
    
    
    model = lambda x, c0, a, w: a * np.exp(-( x - c0 )**2. / w**2.)
    # initial guess 
    max_index = np.where(prob == prob.max())[0][0]
    # guess params freq , amp, width
    p0=np.array([ f[max_index],  prob.max(), (f.max()-f.min())/6.0 ])
    
    fit=curve_fit(model,f,prob,p0=p0)
    
    print "fit params",fit[0]
    print "amplitude is",fit[0][1]
    
    return fit[0][0]



def pi_time_guess(t,p,threshold=0.9):
    # looking for the first 0.8 probability
    temp=p/p.max()
    try:
        first_peak=np.where(temp>threshold)[0][0]
        pi_time=t[first_peak]
    except:
        f = None
        return p.max(), f
    
    #print "pi time", pi_time
    if pi_time == 0 :
        f = None
    else:
        f= 1.0/(2*pi_time)/2
    
    return p.max(), f

def fit_sin(sc,dv, ident):
    
    ds = sc.get_dataset(ident) # needs to be implemented
    data = np.array(get_data(dv,ds))
    
    
    t = data[:,0] 
    y= data[:,-1]
        
    model = lambda  x, a, f: a * np.sin(( 2*np.pi*f*x ))**2
    p0=pi_time_guess(t,y)
    
    
    if p0[1] == None:
        print "pi time is zero -> problem with the fit"
        return None
    
    try:
        popt, copt = curve_fit(model, t, y, p0)
#         print "best fit params" , popt
        f=popt[1]
        pi_time=1.0/f/4
    except:
        "wasn't able to fit this, pi time is set to the guess"
        f =p0[1]
        pi_time=1.0/f/4
        
#     print " pi time is: ", pi_time
    return pi_time

