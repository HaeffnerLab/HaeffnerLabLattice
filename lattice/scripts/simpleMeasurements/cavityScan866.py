import sys; sys.path.append('/home/lattice/LabRAD/lattice/scripts')
import labrad
from scriptLibrary.cavityScan import scanCavity  

cxn = labrad.connect()
cxnlab =  labrad.connect('192.168.169.49')
scanCavity(cxn, cxnlab, ch = '866', resolution = 2, min = 400.0, max = 600.0, average = 3)
print 'DONE'