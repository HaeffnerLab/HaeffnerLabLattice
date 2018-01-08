import  labrad
import numpy as np
import matplotlib.pyplot as plt
from labrad.units import WithUnit as U
from scipy.optimize import curve_fit
 
cxn = labrad.connect()
sc = cxn.scriptscanner
dv = cxn.data_vault
grapher = cxn.grapher 


avg_correction_short_R = np.zeros(4, dtype= float)
avg_correction_long_R= np.zeros(4, dtype= float)
avg_correction_short_L = np.zeros(4, dtype= float)
avg_correction_long_L= np.zeros(4, dtype= float)

# 
def get_data(ds):
    direc, dset = ds[0]
    dv.cd(direc)
    dv.open(dset)
    return dv.get()

def calc_phase(ident,iter = 1.0):
    # get the data
    ds = sc.get_dataset(ident) # needs to be implemented
    data = np.array(get_data(ds))
    
    print data
    
    laser_phase = data[:,0] 
    parity = data[:,-1]
   
    A_short_false=0.3978# this is the con
    A_long_false=0.3722# this is the con
    A_short_true=0.3699 # this is the con
    A_long_true=0.3195 # this is the con


    phase_short_false = 1.0*np.arccos(-(parity[0]-parity[1])/2.0/A_short_false)*180.0/np.pi -90.0 
    phase_long_false =  1.0*np.arccos(-(parity[2]-parity[3])/2.0/A_long_false)*180.0/np.pi -90.0
    phase_short_true =  1.0*np.arccos(-(parity[4]-parity[5])/2.0/A_short_true)*180.0/np.pi -90.0
    phase_long_true =   1.0*np.arccos(-(parity[6]-parity[7])/2.0/A_long_true)*180.0/np.pi -90.0
   
    print " phase_short_false", phase_short_false, "in deg"     
    print " phase_long_false", phase_long_false, "in deg"
    print " phase_short_true", phase_short_true, "in deg"
    print " phase_long_true", phase_long_true, "in deg"
    
    # checking if the phase is nan than set's it 
    if np.isnan(phase_short_false):
        phase_short_false=9999
        correction_short_R = U(phase_short_false,'deg')
        print "problem with the phase calc"
    else:
        p1=sc.get_parameter('LLI','phase_short_false')
        correction_short_R = (p1- U(phase_short_false,'deg')/2.0) 
        avg_correction_short_R[iter % len(avg_correction_short_R)] = correction_short_R['deg']
        print avg_correction_short_R
        print "iter", iter
        # stabilizing on the average 
        if iter>len(avg_correction_short_R):
            print "feedback angle"
            sc.set_parameter('LLI','phase_short_false',U(np.average(avg_correction_short_R),'deg'))
    
    # checking if the phase is nan than set's it 
    if np.isnan(phase_long_false):
        phase_long_false=9999
        correction_long_R = U(phase_long_false,'deg')
        print "problem with the phase calc"
    else:
        p2=sc.get_parameter('LLI','phase_long_false')
        correction_long_R = (p2- U(phase_long_false,'deg')/2.0)
        avg_correction_long_R[iter % len(avg_correction_long_R)] = correction_long_R['deg']
        # stabilizing on the average 
        if iter>len(avg_correction_long_R):
            sc.set_parameter('LLI','phase_long_false', U(np.average(avg_correction_long_R),'deg'))
    
    # checking if the phase is nan than set's it 
    if np.isnan(phase_short_true):
        phase_short_true=9999
        correction_short_L = U(phase_short_true,'deg')
        print "problem with the phase calc"
    else:
        p3=sc.get_parameter('LLI','phase_short_true')
        correction_short_L = (p3- U(phase_short_true,'deg')/2.0)
        
        avg_correction_short_L[iter % len(avg_correction_short_L)] = correction_short_L['deg']
        # stabilizing on the average 
        if iter>len(avg_correction_short_L):
            sc.set_parameter('LLI','phase_short_true',U(np.average(avg_correction_short_L),'deg'))
    
    # checking if the phase is nan than set's it 
    if np.isnan(phase_long_true):
        phase_long_true=9999
        correction_long_L = U(phase_long_true,'deg')
        print "problem with the phase calc"
    else:
        p4=sc.get_parameter('LLI','phase_long_true')
        correction_long_L = (p4- U(phase_long_true,'deg')/2.0)
        
        avg_correction_long_L[iter % len(avg_correction_long_L)] = correction_long_L['deg']
        # stabilizing on the average 
        if iter>len(avg_correction_long_L):
            sc.set_parameter('LLI','phase_long_true',U(np.average(avg_correction_long_L),'deg'))
     
#     print "the new phase should be", (p1['deg']+ phase_short_false/2)
    
    return correction_short_R['deg'] , correction_long_R['deg'] , correction_short_L['deg'] , correction_long_L['deg']

def setup_Experiment(  name , scan,parameter_to_scan ='param', num_of_params_to_sub =4):
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
        dependents = [('', ' phase {}'.format(x), '') for x in range(num_of_params_to_sub)]
                
        ds = dv.new( timetag ,[(parameter_to_scan, '')],dependents, context = data_save_context )
        
        
        if grapher is not None: 
            window = 'ramsey'           
            grapher.plot_with_axis(ds, window, scan) # -> plot_with_axis
        
        return data_save_context




# initlizing data vault

# modify new_sequence to take a list of override parameters

scan = [('LLI_PhaseMeasurement',   ('Dummy.dummy_detuning', 0, 7, 1.0, 'deg'))]

t_min , t_max , step_size = 1.0, 500.0, 1.0
temp_ts=np.arange(t_min,t_max,step_size)
 
ts = [ U(x,'us') for i,x in enumerate(temp_ts)]

data_save_context=setup_Experiment( "LLI_phase_measurement" ,  ts , parameter_to_scan ='time' )

phase_short_R = np.zeros_like(ts, dtype=float)
phase_long_R = np.zeros_like(ts, dtype=float)
phase_short_L = np.zeros_like(ts, dtype=float)
phase_long_L = np.zeros_like(ts, dtype=float)

for i,t in enumerate(ts):
    print "Scanning iteration" , t
    print t
    # scan the heating time
    #sc.set_parameter('LLI','wait_time',t)
    
    ident = sc.new_sequence('LLI_PhaseMeasurement', scan)
    print " scan_ident",ident
    sc.sequence_completed(ident) # wait until sequence is completed
    phase_short_R[i] , phase_long_R[i], phase_short_L[i] , phase_long_L[i] =calc_phase(ident , iter = i)
    
    submission = [t['us']]
    submission.extend([phase_short_R[i] , phase_long_R[i], phase_short_L[i] , phase_long_L[i]] )
    dv.add(submission, context = data_save_context)


#sc.set_parameter('LLI','wait_time',U(0.0,'us'))
   
#np.savetxt('HeatingRate.csv', (ts,nbar),  delimiter=',')
cxn.disconnect()

