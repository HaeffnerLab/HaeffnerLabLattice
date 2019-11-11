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

def calc_phase(ident):
    # get the data
    ds = sc.get_dataset(ident) # needs to be implemented
    data = np.array(get_data(ds))
    
#     print data
    
    laser_phase = data[:,0] 
    prob = data[:,-1]
    ind1 = np.where(laser_phase == 0.0)
    ind2 = np.where(laser_phase == 90.0)
        
    p1 =prob[ind1]
    p2 =prob[ind2]
    A=0.4 # this is the con
    phase = 1.0*np.arccos(-(p1-p2)/(2.0*A))*180.0/np.pi #1.0*np.arcsin((p1-p2))*180.0/np.pi
        
    print "at laser_phase ",laser_phase[ind1], " the parity is", p1  
    print "at laser_phase ",laser_phase[ind2], " the parity is", p2
    print " the calculated phase", phase, "in deg"     
  
    return data[:,-1]#phase


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
        dependents = [('', ' parity {}'.format(x), '') for x in range(num_of_params_to_sub)]
                
        ds = dv.new( timetag ,[(parameter_to_scan, '')],dependents, context = data_save_context )
        
        
        if grapher is not None: 
            window = 'ramsey'           
            grapher.plot_with_axis(ds, window, scan) # -> plot_with_axis
        
        return data_save_context




# initlizing data vault

# modify new_sequence to take a list of override parameters

scan = [('LLI_StatePreparation',   ('LLI.phase', 0, 90, 45, 'deg'))]

t_min , t_max , step_size = 1.0, 100.0, 1.0
temp_ts=np.arange(t_min,t_max,step_size)
# temp_ts=np.arange(t_min,t_max,step_size)
# temp_ts=np.append(temp_ts, t_max)
# 
# print temp_ts   
# # shuffeling the wait times
# #np.random.shuffle(temp_ts)  
# 
ts = [ U(x,'us') for i,x in enumerate(temp_ts)]

wait_times = np.array([5,50,100])*1000

data_save_context=setup_Experiment( "LLI_phase_measurement" , ts , parameter_to_scan ='time', num_of_params_to_sub =2*3*len(wait_times))

for i,t in enumerate(ts):
    print "Scanning iteration" , t
    print t
    
    parity_R=[]#np.zeros(2*len(wait_times))
    
    # set the wait_time
    sc.set_parameter('LLI','flip_optical_pumping', False)
    for j,wait_time in enumerate(wait_times):
        print "Scanning wait_time" , wait_time
        sc.set_parameter('LLI','wait_time', U(wait_time,'us'))
        ident = sc.new_sequence('LLI_StatePreparation', scan)
        print " scan_ident",ident
        sc.sequence_completed(ident) # wait until sequence is completed
        #parity_R[2*j:(2*j+1+1)]=calc_phase(ident)
        parity_R.extend(calc_phase(ident))
        
    submission = [t['us']]
    submission.extend(parity_R)
    
    
    parity_L=[]
    # set the wait_time
    sc.set_parameter('LLI','flip_optical_pumping', True)
    for j,wait_time in enumerate(wait_times):
        print "Scanning wait_time" , wait_time
        sc.set_parameter('LLI','wait_time', U(wait_time,'us'))
        ident = sc.new_sequence('LLI_StatePreparation', scan)
        print " scan_ident",ident
        sc.sequence_completed(ident) # wait until sequence is completed
        parity_L.extend(calc_phase(ident))
     

    submission.extend(parity_L)
    print " this is the submission L",submission
    dv.add(submission, context = data_save_context)
    
    


#sc.set_parameter('LLI','wait_time',U(0.0,'us'))
   
#np.savetxt('HeatingRate.csv', (ts,nbar),  delimiter=',')
cxn.disconnect()

#print wait_time, rsb_peak
# plt.plot(ts,nbar,'r',label='fring contrast')
# plt.xlabel('wait_time [us]')
# plt.ylabel('fring contrast')
# plt.show()