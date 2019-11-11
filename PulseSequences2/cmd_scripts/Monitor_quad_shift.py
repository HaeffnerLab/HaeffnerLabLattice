import  labrad
import numpy as np
import matplotlib.pyplot as plt
from labrad.units import WithUnit as U
from scipy.optimize import curve_fit
from AnalysisTools import fit_gaussian, fit_sin

 
cxn = labrad.connect()
sc = cxn.scriptscanner
dv = cxn.data_vault
dt = cxn.sd_tracker
grapher = cxn.grapher 

   
def setup_Experiment(  name , scan,parameter_to_scan ='param', num_of_params_to_sub =6):
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

scan_Spectrum = [('Spectrum',   ('Spectrum.carrier_detuning', -3, 4, 0.5, 'kHz'))]
scan_Rabi_1 = [('RabiFlopping',   ('RabiFlopping.duration', 0, 25, 1, 'us'))]
scan_Rabi_2 = [('RabiFlopping',   ('RabiFlopping.duration', 0, 45, 2, 'us'))]

t_min , t_max , step_size = 1.0, 100.0, 1.0
temp_ts=np.arange(t_min,t_max,step_size)
 
ts = [ U(x,'us') for i,x in enumerate(temp_ts)]

data_save_context=setup_Experiment( "Monitor_quad_shift" ,  ts , parameter_to_scan ='time' )

phase_short_R = np.zeros_like(ts, dtype=float)

i=0
while True:
    print "Scanning iteration" , i
        
    sc.set_parameter('Spectrum', 'selection_sideband','axial_frequency')
    ident = sc.new_sequence('Spectrum',scan_Spectrum)
    print " scan_ident",ident
    sc.sequence_completed(ident) # wait until sequence is completed
     
    axial_frequenc_com = fit_gaussian(sc,dv,ident)*1000.0
    print "axial frequency: ", axial_frequenc_com , "kHz" 
    
    sc.set_parameter('Spectrum', 'selection_sideband','aux_axial')
    ident = sc.new_sequence('Spectrum',scan_Spectrum)
    print " scan_ident",ident
    sc.sequence_completed(ident) # wait until sequence is completed
    axial_frequency_stretch = fit_gaussian(sc,dv,ident)*1000.0
    print "axial frequency: ", axial_frequency_stretch , "kHz" 
    
    sc.set_parameter('RabiFlopping','line_selection','S-1/2D-1/2')
    ident = sc.new_sequence('RabiFlopping',scan_Rabi_1)
    print " scan_ident",ident
    sc.sequence_completed(ident) # wait until sequence is completed
    
    pi_time_1 = fit_sin(sc,dv, ident)
    print "pi_time: ", pi_time_1 , "us" 
    
    sc.set_parameter('RabiFlopping','line_selection','S-1/2D-3/2')
    ident = sc.new_sequence('RabiFlopping',scan_Rabi_2)
    print " scan_ident",ident
    sc.sequence_completed(ident) # wait until sequence is completed
    
    pi_time_2 = fit_sin(sc,dv, ident)
    print "pi_time: ", pi_time_2 , "us" 
    
    sc.set_parameter('RabiFlopping','line_selection','S-1/2D-5/2')
    ident = sc.new_sequence('RabiFlopping',scan_Rabi_2)
    print " scan_ident",ident
    sc.sequence_completed(ident) # wait until sequence is completed
    
    pi_time_3 = fit_sin(sc,dv, ident)
    print "pi_time: ", pi_time_3 , "us" 
    
    B_field = dt.get_b_field()[0]
               
    submission = [i]
    
    
    submission.extend([B_field, axial_frequenc_com,axial_frequency_stretch, pi_time_1 , pi_time_2, pi_time_3] )
    dv.add(submission, context = data_save_context)
    print " submission", submission
    i=i+1

#sc.set_parameter('LLI','wait_time',U(0.0,'us'))
   
#np.savetxt('HeatingRate.csv', (ts,nbar),  delimiter=',')
cxn.disconnect()

