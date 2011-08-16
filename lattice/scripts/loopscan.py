import labrad
import time
import numpy
ld = labrad.connect().laserdac

MIN = 750.0
MAX = 850.0
RESOLUTION = 1 #resolution in millivolts
CHANNEL = '397S'
SLEEP = .03
current = ld.getvoltage(CHANNEL)
print 'current value: %.3f' % current

for voltage in numpy.arange(current,MIN,RESOLUTION):
    ld.setvoltage(CHANNEL,voltage)

while True:
    print 'going up'
    for voltage in numpy.arange(MIN,MAX,RESOLUTION):
        ld.setvoltage(CHANNEL,voltage, wait = False)
        time.sleep(SLEEP)
    print 'going down'
    for voltage in numpy.arange(MIN,MAX,RESOLUTION)[::-1]:
        ld.setvoltage(CHANNEL,voltage, wait = False)
        time.sleep(SLEEP)
