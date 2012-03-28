
import labrad
import numpy
import time
from msvcrt import getch, kbhit

cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
rf = cxn.lattice_pc_hp_server
ld = cxnlab.laserdac
pulser = cxn.pulser

def kbfunc():
    x = kbhit()
    if x:
        ret = getch()
    else:
        ret = 0
    return ret

ch = '397'
initcavity = ld.getvoltage(ch) 
initpower = rf.getpower()
min = initcavity - 20

print 're-crystallization script running..'
print initcavity, min, initpower

while 1:
	key = kbfunc()
	if key == "\x1b":
    		print 'Resetting rf & Switching on far-red beam..'		
		time.sleep(0.5)
    		rf.setpower(-5.9)
		pulser.switch_manual('crystallization',  True) # crystallization shutter open
		pulser.switch_manual('110DP',  False) # 110DP off         
   		#for voltage in numpy.arange(initcavity, min, -1):
   		 #   print voltage
   		 #   time.sleep(0.05)
   		 #   ld.setvoltage(ch,voltage)