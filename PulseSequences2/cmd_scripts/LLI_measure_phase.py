import  labrad
import numpy as np
import matplotlib.pyplot as plt
from labrad.units import WithUnit as U
from scipy.optimize import curve_fit
import time
 
cxn = labrad.connect()
sc = cxn.scriptscanner
dv = cxn.data_vault
dt = cxn.sd_tracker
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

# def calc_contrast(ident):
#     
#     # get the data
#     ds = sc.get_dataset(ident) # needs to be implemented
#     data = np.array(get_data(ds))
#     
#        
#     laser_phase = data[:,0] 
#     parity = data[:,-1]
#     print "parity data"
#     print parity
#     contrast = (parity[0]-parity[1])/2.0
#     print "contrast is: " , contrast
#     
#     return 
   

    

def calc_phase(ident,iter = 1.0):
    # get the data
    ds = sc.get_dataset(ident) # needs to be implemented
    data = np.array(get_data(ds))
    
#     print data
    
    laser_phase = data[:,0] 
    parity = data[:,-1]
    
    if len(laser_phase) > 7:
        print "calculating the parity "
        print parity[-2], parity[-1]
        contrast = 0.5*(parity[-2]-parity[-1])*100.0
    else:
        contrast=-200.0
   
    A_short_false=0.78# this is the con
    A_long_false= 0.6# this is the con
    A_short_true= 0.75 # this is the con
    A_long_true= 0.5# this is the con


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
        sc.set_parameter('LLI','phase_short_false',correction_short_R)
#         avg_correction_short_R[iter % len(avg_correction_short_R)] = correction_short_R['deg']
#         print avg_correction_short_R
#         print "iter", iter
#         # stabilizing on the average 
#         if iter>len(avg_correction_short_R):
#             print "feedback angle"
#             sc.set_parameter('LLI','phase_short_false',U(np.average(avg_correction_short_R),'deg'))
    
    # checking if the phase is nan than set's it 
    if np.isnan(phase_long_false):
        phase_long_false=9999
        correction_long_R = U(phase_long_false,'deg')
        print "problem with the phase calc"
    else:
        p2=sc.get_parameter('LLI','phase_long_false')
        correction_long_R = (p2- U(phase_long_false,'deg')/2.0)
        sc.set_parameter('LLI','phase_long_false', correction_long_R)
#         
#         avg_correction_long_R[iter % len(avg_correction_long_R)] = correction_long_R['deg']
#         # stabilizing on the average 
#         if iter>len(avg_correction_long_R):
#             sc.set_parameter('LLI','phase_long_false', U(np.average(avg_correction_long_R),'deg'))
    
    # checking if the phase is nan than set's it 
    if np.isnan(phase_short_true):
        phase_short_true=9999
        correction_short_L = U(phase_short_true,'deg')
        print "problem with the phase calc"
    else:
        p3=sc.get_parameter('LLI','phase_short_true')
        correction_short_L = (p3- U(phase_short_true,'deg')/2.0)
        sc.set_parameter('LLI','phase_short_true',correction_short_L)
#         avg_correction_short_L[iter % len(avg_correction_short_L)] = correction_short_L['deg']
#         # stabilizing on the average 
#         if iter>len(avg_correction_short_L):
#             sc.set_parameter('LLI','phase_short_true',U(np.average(avg_correction_short_L),'deg'))
    
    # checking if the phase is nan than set's it 
    if np.isnan(phase_long_true):
        phase_long_true=9999
        correction_long_L = U(phase_long_true,'deg')
        print "problem with the phase calc"
    else:
        p4=sc.get_parameter('LLI','phase_long_true')
        correction_long_L = (p4- U(phase_long_true,'deg')/2.0)
        sc.set_parameter('LLI','phase_long_true',correction_long_L)
#         
#         avg_correction_long_L[iter % len(avg_correction_long_L)] = correction_long_L['deg']
#         # stabilizing on the average 
#         if iter>len(avg_correction_long_L):
#             sc.set_parameter('LLI','phase_long_true',U(np.average(avg_correction_long_L),'deg'))
     
#     print "the new phase should be", (p1['deg']+ phase_short_false/2)
    
    return correction_short_R['deg'] , correction_long_R['deg'] , correction_short_L['deg'] , correction_long_L['deg'] , contrast

def setup_Experiment(  name , scan,parameter_to_scan ='param', num_of_params_to_sub =6):
        # paramter to scan
        # sets up the data vault 
        # setup the grapher
        
        
        #dv = cxn.dv 
        #grapher = cxn.grapher
        
        localtime = time.localtime()
        timetag = time.strftime('%H%M_%S', localtime)
        directory = ['', 'Experiments', time.strftime('%Y%m%d', localtime), name, timetag]
        data_save_context = cxn.context()       
        dv.cd(directory, True, context = data_save_context)
        
        # creating the col names in the output file
        dependents = [('', ' phase {}'.format(x), '') for x in range(num_of_params_to_sub-2)]
        dependents.append(('', ' b field', ''))
        dependents.append(('', ' contrast', ''))
                
        ds = dv.new( timetag ,[(parameter_to_scan, '')],dependents, context = data_save_context )
        
        
        if grapher is not None: 
            window = 'ramsey'           
            grapher.plot_with_axis(ds, window, scan) # -> plot_with_axis
        
        return data_save_context




# initlizing data vault

# modify new_sequence to take a list of override parameters

scan = [('LLI_PhaseMeasurement',   ('Dummy.dummy_detuning', 0, 9, 1.0, 'deg'))]
spectrun_scan = [('Spectrum',   ('Spectrum.carrier_detuning', -4, 4, 0.5, 'kHz'))]
# short_scan = [('LLI_PhaseMeasurement',   ('Dummy.dummy_detuning', 0, 1, 1.0, 'deg'))]

t_min , t_max , step_size = 300.0, 5000.0, 1.0
temp_ts=np.arange(t_min,t_max,step_size)
 
ts = [ U(x,'us') for i,x in enumerate(temp_ts)]

data_save_context=setup_Experiment( "LLI_phase_measurement" ,  ts , parameter_to_scan ='time' )

phase_short_R = np.zeros_like(ts, dtype=float)
phase_long_R = np.zeros_like(ts, dtype=float)
phase_short_L = np.zeros_like(ts, dtype=float)
phase_long_L = np.zeros_like(ts, dtype=float)
contrast = np.zeros_like(ts, dtype=float)

# starting time
localtime = time.localtime()
scan_H = time.strftime('%H', localtime)

for i,t in enumerate(ts):
    print "Scanning iteration" , t
    print t, i
    # scan the heating time
    #sc.set_parameter('LLI','wait_time',t)
    localtime = time.localtime()
    currnet_H = time.strftime('%H', localtime)
    
    if scan_H != currnet_H:
        
        scan_H=currnet_H
        print " starting a new data set"
        # open a new data scan
        data_save_context=setup_Experiment( "LLI_phase_measurement" ,  ts , parameter_to_scan ='time' )
        # calibrate the axial frequency?
        ident = sc.new_sequence('Spectrum', spectrun_scan)
        print " scanning the axial freq"
        print " scan_ident",ident
        sc.sequence_completed(ident) # wait until sequence is completed
    
    ident = sc.new_sequence('LLI_PhaseMeasurement', scan)
    print " scan_ident",ident
    sc.sequence_completed(ident) # wait until sequence is completed
    phase_short_R[i] , phase_long_R[i], phase_short_L[i] , phase_long_L[i] , contrast[i] = calc_phase(ident , iter = i)
    b_field = dt.get_b_field()[0]
    submission = [t['us']]
    submission.extend([phase_short_R[i] , phase_long_R[i], phase_short_L[i] , phase_long_L[i], b_field, contrast[i]] )
    dv.add(submission, context = data_save_context)

#     # running every x iteration to check the contrast
#     if (i % 10000)==0:
#         print " measuring the contrast"
#         p1=sc.get_parameter('LLI','phase_short_false')
#         sc.set_parameter('LLI','phase_short_false',p1+ U(45.0,'deg')) 
#         
#         ident = sc.new_sequence('LLI_PhaseMeasurement', short_scan)
#         print " scan_ident",ident
#         sc.sequence_completed(ident) # wait until sequence is completed
#         calc_contrast(ident)
#         print " Going back to LLI measure"
#         # setting the angles back to the continue the measurement 
#         sc.set_parameter('LLI','phase_short_false',p1) 

        

#sc.set_parameter('LLI','wait_time',U(0.0,'us'))
   
#np.savetxt('HeatingRate.csv', (ts,nbar),  delimiter=',')
cxn.disconnect()

