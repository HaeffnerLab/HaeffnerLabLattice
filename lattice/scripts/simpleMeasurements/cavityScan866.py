import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
from scriptLibrary.cavityScan import scanCavity  

cxn = labrad.connect()
scanCavity(cxn, ch = '866', resolution = 2, min = 460.0, max = 640.0, average = 3)
print 'DONE'