import labrad
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49')
try:
    dv = cxn.data_vault
except Exception:
    pass
try:
    pulser = cxn.pulser
except Exception:
    pass
try:
    n = cxn.node_lattice_control
except Exception:
    pass
