import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
from scriptLibrary.cavityScan import scanCavity  

cxn = labrad.connect()
scanCavity(cxn, ch = '866', resolution = 2, min = 475.0, max = 625.0, average = 3)
print 'DONE'