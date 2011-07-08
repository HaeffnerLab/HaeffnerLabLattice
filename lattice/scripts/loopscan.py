import labrad
import time
import numpy
ld = labrad.connect().laserdac

MIN = 800.0
MAX = 900.0
RESOLUTION = 1 #resolution in millivolts
CHANNEL = '397'
SLEEP = .01
current = ld.getcavity(CHANNEL)
print 'current value: %.3f' % current

for voltage in numpy.arange(current,MIN,RESOLUTION):
    ld.setcavity(CHANNEL,voltage)

while True:
    print 'going up'
    for voltage in numpy.arange(MIN,MAX,RESOLUTION):
        ld.setcavity(CHANNEL,voltage, wait = False)
        time.sleep(SLEEP)
    print 'going down'
    for voltage in numpy.arange(MIN,MAX,RESOLUTION)[::-1]:
        ld.setcavity(CHANNEL,voltage, wait = False)
        time.sleep(SLEEP)
