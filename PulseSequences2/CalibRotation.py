from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

#class RabiFloppingMulti(pulse_sequence):
#    is_multi = True
#    sequences = [RabiFlopping, Spectrum]

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

def fit_sin(t,data):
    from scipy.optimize import curve_fit
    
    model = lambda  x, a, f: a * np.sin(( 2*np.pi*f*x ))**2
    p0=pi_time_guess(t,data)
    
    
    if p0[1] == None:
        print "pi time is zero -> problem with the fit"
        return None
    
    try:
        popt, copt = curve_fit(model, t, data, p0)
#         print "best fit params" , popt
        f=popt[1]
        pi_time=1.0/f/4
    except:
        "wasn't able to fit this, pi time is set to the guess"
        f =p0[1]
        pi_time=1.0/f/4
        
#     print " pi time is: ", pi_time
    return pi_time

def DataSort(All_data, num_of_ions):
    
    data_out=np.zeros([num_of_ions,len(All_data)])
    
    for i in range(len(All_data)):
        data_out[:,i]=All_data[i]
    return data_out


class CalibRotation(pulse_sequence):
    scannable_params = {
        'RabiFlopping.duration':  [(0., 50., 25.0, 'us'), 'rabi']
        #'Excitation_729.rabi_excitation_duration' : [(-150, 150, 10, 'kHz'),'spectrum'],
              }

    show_params= [
                  
                  'RabiFlopping.line_selection',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',

                  ]
    
    #fixed_params = {'StateReadout.ReadoutMode':'camera'}



    def sequence(self):
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        ## calculate the scan params
        rf = self.parameters.RabiFlopping 
        
        #freq_729=self.calc_freq(rf.line_selection)
        freq_729=self.calc_freq(rf.line_selection , rf.selection_sideband , rf.order)
        channel_729 = self.parameters.Excitation_729.channel_729
        
        print "Rabi flopping 729 freq is {}".format(freq_729)
        print "Rabi flopping duration is {}".format(rf.duration)
        # building the sequence
        self.end = U(10., 'us')
        #self.addSequence(TurnOffAll)
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        #self.addSequence(RabiExcitation)     
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729':channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': rf.rabi_amplitude_729,
                                         'Excitation_729.rabi_excitation_duration':  rf.duration })
        self.addSequence(StateReadout)
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
   
    
    @classmethod
    def run_finally(cls, cxn, parameters_dict, data, t):
        
        
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        # for the multiple case we summ the probabilities, this also
        # reduces the dimension to 1 for single ion case 
        all_data=np.array(data)
        
#         try:
#                 all_data = all_data.sum(1)
#             except ValueError:
#                 return
#       
      
          
        if parameters_dict.StateReadout.readout_mode =='pmt':
            all_data = all_data.sum(1)
            pi_time=fit_sin(t,all_data)
            print " pi time is: ", pi_time
            
        elif parameters_dict.StateReadout.readout_mode =='camera':
            num_of_ions=int(parameters_dict.IonsOnCamera.ion_number)
            all_data=DataSort(all_data,num_of_ions)
#             print all_data
            for i in range(num_of_ions):
#                 
                pi_time=fit_sin(t,all_data[i,:])
                print "ion",i, "pi time is:" , pi_time
           
          
        
        

        
        # add the setting of the value for the pi time
        
