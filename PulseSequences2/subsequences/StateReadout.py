from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
#from treedict import TreeDict

class StateReadout(pulse_sequence):
    '''
    Pulse sequence for reading out the state of the ion. 
    '''
   
    def sequence(self):
        
       
        st = self.parameters.StateReadout 
        repump_additional = self.parameters.DopplerCooling.doppler_cooling_repump_additional# need the doppler paramters for the additional repumper time 
        
        # fic the readout duration according to PMT/Camera        
        if st.use_camera_for_readout:
            readout_duration=st.camera_readout_duration
        else:
            readout_duration=st.pmt_readout_duration
        
        # sending the camera trigger and adjusting the times       
        if st.use_camera_for_readout:
            self.addTTL('camera', self.start, st.camera_trigger_width)
            # adding 2 milli sec to allow the camera transfer
            duration_397=readout_duration + st.camera_transfer_additional 
            duration_866=readout_duration + st.camera_transfer_additional + repump_additional
        else:
            # removing the additional time for the camera transfer
            duration_397=readout_duration
            duration_866=readout_duration + repump_additional
        
        self.addTTL('ReadoutCount', self.start, readout_duration)
        
        self.addDDS ('397',self.start, duration_397, st.state_readout_frequency_397, st.state_readout_amplitude_397)
        #self.addDDS ('866',self.start, duration_866, st.state_readout_frequency_866, st.state_readout_amplitude_866)
        # changing the 866 from a dds to a rf source enabled by a switch
        self.addTTL('866DP', self.start+ WithUnit(0.25, 'us'), duration_866- WithUnit(0.1, 'us') )
                    
        self.end = self.start + duration_866
        print "State Readout" 
#         print "State readout"
#         print "397 amp.{}".format(st.state_readout_amplitude_397)
        