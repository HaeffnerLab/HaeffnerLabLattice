import labrad
from scripts.scriptLibrary.cavityScan import scanCavity  

cxn = labrad.connect()
cxnlab =  labrad.connect('192.168.169.49')
scanCavity(cxn, cxnlab,ch = '397', resolution = 1.0, min = 350.0, max = 351.0, average = 3)