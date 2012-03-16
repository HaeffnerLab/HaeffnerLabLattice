import labrad
import numpy
import time
cxn = labrad.connect()
pulser = cxn.pulser
#demo manual switching
#print pulser
#print pulser.get_channels()
#pulser.switch_manual('866DP', False)
#pulser.switch_manual('axial', True)
#sequence done?
#print pulser.wait_sequence_done()

#demo pulse sequence
#pulser.new_sequence()
#duration = .1
#channels = pulser.get_channels()
#
#for i in range(len(channels)):
#    pulser.add_ttl_pulse(channels[i],  i * duration, duration)
#
#pulser.program_sequence()
#pulser.start_infinite()
#pulser.start()
#seq =  pulser.human_readable().asarray
#print seq

#diff mode
#pulser.new_sequence()
#countRate = .1
#pulser.add_ttl_pulse('DiffCountTrigger', 0.0, 10.0e-6)
#pulser.add_ttl_pulse('DiffCountTrigger', countRate, 10.0e-6)
#pulser.add_ttl_pulse('866DP', 0.0, countRate)
#pulser.extend_sequence_length(2*countRate)
##pulser.add_ttl_pulse('fake', 2*countRate, 10.0e-6)
#pulser.program_sequence()
##pulser.start_infinite()
#pulser.start_single()
#print 'started'
#time.sleep(3)
#print 'stopping'
#pulser.stop_sequence()

#time resolved counting
pulser.new_sequence()
pulser.add_ttl_pulse('TimeResolvedCount', 0.0, 1.0)
pulser.add_ttl_pulse('866DP', 0.0, 1.0)
pulser.program_sequence()
pulser.reset_timetags()
pulser.start_single()
pulser.wait_sequence_done()
pulser.stop_sequence()
timetags = pulser.get_timetags().asarray
print timetags