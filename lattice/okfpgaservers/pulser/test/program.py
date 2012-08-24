import labrad
from labrad import types as T
import time
cxn = labrad.connect()
pulser = cxn.pulser

pulser.new_sequence()
#program 1000 pulses
#old way
tinit = time.time()
total = 500
iters = 1
for i in range(iters):
    print 'i'
    periter = total / iters
    pulses = [(T.Value((periter*i + t)/1000.0,'s'), T.Value(80.0, 'MHz'), T.Value(-63.0, 'dBm')) for t in range(1, periter)]
    pulser.add_dds_pulses(('866DP', pulses))
print time.time() - tinit
tinit = time.time()
pulser.program_sequence()
print time.time() - tinit