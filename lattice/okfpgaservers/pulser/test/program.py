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
iters = 5
for i in range(iters):
    pulses = [(T.Value((100*i + t)/1000.0,'s'), T.Value(80.0, 'MHz'), T.Value(-63.0, 'dBm')) for t in range(1,total / iters)]
    pulser.add_dds_pulses(('866DP', pulses))
pulser.program_sequence()
print time.time() - tinit