import labrad
import numpy
cxn = labrad.connect()
pulser = cxn.pulser
#demo manual switching
#print pulser
#print pulser.get_channels()
#pulser.switch_manual('866DP', False)
#pulser.switch_manual('axial', True)
#sequence done?
#print pulser.wait_sequence_done()

'''normal counting'''


#demo pulse sequence
#pulser.new_sequence()
#duration = .1
#for i in range(8):
#    pulser.add_ttl_pulse(str(i),  i * duration, duration)
#pulser.add_ttl_pulse('31',  .5 * duration, duration)
##pulser.program_sequence()
##pulser.start_infinite()
##pulser.start()
#print 'trying to get'
#seq =  pulser.human_readable().asarray
#print seq