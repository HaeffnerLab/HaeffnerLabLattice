import labrad
from labrad import types as T
cxn = labrad.connect()
pulser = cxn.pulser
pulser.new_sequence()
#program 1000 pulses
#old way
p = []
p.append(('866DP', T.Value(100, 'us'), T.Value(100, 'us'), T.Value(80, 'MHz'), T.Value(-33.0, 'dBm')))
p.append(('854DP', T.Value(50, 'us'), T.Value(51, 'us'), T.Value(80, 'MHz'), T.Value(-33.0, 'dBm')))
pulser.add_dds_pulses(p)
pulser.program_sequence()