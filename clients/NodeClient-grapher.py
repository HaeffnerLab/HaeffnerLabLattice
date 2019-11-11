import labrad
try:
    cxn = labrad.connect()
except Exception:
    print "Please start LabRAD manager"
else:
    node = 'node_lattice_control'
    cxn.servers[node].start('Real Simple Grapher')
