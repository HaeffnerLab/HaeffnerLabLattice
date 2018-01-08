import  labrad
import numpy as np
import matplotlib.pyplot as plt
from labrad.units import WithUnit as U
from scipy.optimize import curve_fit
 
cxn = labrad.connect()
sc = cxn.scriptscanner
dv = cxn.data_vault
grapher = cxn.grapher 
# 
def get_data(ds):
    direc, dset = ds[0]
    dv.cd(direc)
    dv.open(dset)
    return dv.get()



def find_peak(ident):
    # get the data
    ds = sc.get_dataset(ident) # needs to be implemented
    data = np.array(get_data(ds))
    
    f = data[:,0] 
    prob = data[:,1]
    model = lambda x, c0, a, w: a * np.exp(-( x - c0 )**2. / w**2.)
    # initial guess 
    max_index = np.where(prob == prob.max())[0][0]
    # guess params freq , amp, width
    p0=np.array([ f[max_index],  prob.max(), (f.max()-f.min())/6.0 ])
    
    fit=curve_fit(model,f,prob,p0=p0)
    
    print "fit params",fit[0]
    print "finished scanning time " , t
    print "amplitude is",fit[0][1]
    
    return fit[0][1]

def setup_Experiment(  name , scan,parameter_to_scan ='param', num_of_params_to_sub =1):
        # paramter to scan
        # sets up the data vault 
        # setup the grapher
        import time
        
        #dv = cxn.dv 
        #grapher = cxn.grapher
        
        localtime = time.localtime()
        timetag = time.strftime('%H%M_%S', localtime)
        directory = ['', 'Experiments', time.strftime('%Y%m%d', localtime), name, timetag]
        data_save_context = cxn.context()       
        dv.cd(directory, True, context = data_save_context)
        
        # creating the col names in the output file
        dependents = [('', ' n bar {}'.format(x), '') for x in range(num_of_params_to_sub)]
                
        ds = dv.new( timetag ,[(parameter_to_scan, '')],dependents, context = data_save_context )
        
        
        if grapher is not None: 
            window = 'current'           
            grapher.plot_with_axis(ds, window, scan) # -> plot_with_axis
        
        return data_save_context




# initlizing data vault

# modify new_sequence to take a list of override parameters

scan_1 = [('LLI_StatePreparation',   ('LLI.wait_time', 4, 10, 0.04, 'ms'))]
scan_2 = [('LLI_StatePreparation',   ('LLI.wait_time', 10, 20, 0.04, 'ms'))]




t_min , t_max , step_size = 0.0, 40000.0, 5000.0



temp_ts=np.arange(t_min,t_max,step_size)
temp_ts=np.append(temp_ts, t_max)

print temp_ts   
# shuffeling the wait times
np.random.shuffle(temp_ts)  

ts = [ U(x,'us') for i,x in enumerate(temp_ts)]

data_save_context=setup_Experiment( "HeatingRate" ,  ts , parameter_to_scan ='heating_time' )



rsb_peak=np.zeros_like(ts)
bsb_peak=np.zeros_like(ts)
nbar=np.zeros_like(ts)
wait_time=np.zeros_like(ts)
for i,t in enumerate(ts):
    print "Scanning heating time" , t
    # scan the heating time
    sc.set_parameter('Heating','background_heating_time',t)
    
    # scan the redsideband first
    sc.set_parameter('Spectrum','order',-1.0)
    
    ident = sc.new_sequence('Spectrum', scan)
    print "scheduled the sequence -> redsidbend"
    sc.sequence_completed(ident) # wait until sequence is completed
    rsb_peak[i]=find_peak(ident)
    
    # scan the bluesideband
    sc.set_parameter('Spectrum','order',1.0)
      
    ident = sc.new_sequence('Spectrum', scan)
    print "scheduled the sequence  -> bluesidbend"
    sc.sequence_completed(ident) # wait until sequence is completed
    bsb_peak[i]=find_peak(ident)
      
    R=1.0*rsb_peak[i]/bsb_peak[i]
    nbar[i]=1.0*R/(1.0-1.0*R)
    print " n_bar", nbar[i]
    wait_time[i]=t['us']
    submission = [t['us'], nbar[i]]
    dv.add(submission, context = data_save_context)

sc.set_parameter('Heating','background_heating_time',U(0.0,'us'))
sc.set_parameter('Spectrum','order',0.0)   
#np.savetxt('HeatingRate.csv', (ts,nbar),  delimiter=',')
cxn.disconnect()

print wait_time, rsb_peak
# plt.plot(ts,nbar,'r',label='fring contrast')
# plt.xlabel('wait_time [us]')
# plt.ylabel('fring contrast')
# plt.show()