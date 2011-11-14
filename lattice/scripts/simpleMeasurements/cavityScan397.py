import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
from scriptLibrary.cavityScan import scanCavity  

cxn = labrad.connect()
scanCavity(cxn, ch = '397', resolution = 1.0, min = 325.0, max = 410.0, average = 3)
