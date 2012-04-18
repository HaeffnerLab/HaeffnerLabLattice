
import labrad
import numpy
import time
from msvcrt import getch, kbhit

cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
rf = cxn.trap_drive
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
initpower = rf.amplitude()
min = initcavity - 20

print 're-crystallization script running..'
print initcavity, min, initpower

while 1:
	key = kbfunc()
	#initpower = rf.amplitude()
	if key == "\r": #\x1b
    		print 'Resetting rf & Switching on far-red beam..'		
		time.sleep(0.1)
    		rf.amplitude(-7.0)
		pulser.switch_manual('crystallization',  True) # crystallization shutter open
		pulser.switch_manual('110DP',  False) # 110DP off 
		time.sleep(2)	
		pulser.switch_manual('110DP',  True)
		#pulser.switch_manual('crystallization',  False)
		rf.amplitude(initpower)
   		#for voltage in numpy.arange(initcavity, min, -1):
   		 #   print voltage
   		 #   time.sleep(0.05)
   		 #   ld.setvoltage(ch,voltage)
