import labrad
from scripts.scriptLibrary.cavityScan import scanCavity  

cxn = labrad.connect()
cxnlab =  labrad.connect('192.168.169.49')
scanCavity(cxn, cxnlab, ch = '866', resolution = 2, min =500.0, max = 700.0, average = 3)
print 'DONE'