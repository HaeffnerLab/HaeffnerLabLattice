import labrad
import time
import numpy as np

# connect to local labrad
cxn = labrad.connect()

# connect to labrad in laserroom
b = labrad.connect('192.168.169.49')


# how to change things in pulser

#a.pulser.amplitude('729DP', WithUnit(-5, 'dBm'))

#b.laserdac.getvoltage('397')

# voltage in setvoltage is in mV
#b.laserdac.setvoltage('397', 326)

print "\n\n"

# switch on blue PI
cxn.pulser.switch_manual('bluePI', True)
time.sleep(1.0)

threshold = 5.0

counts = 0.0

# checking frequency of 422
b.multiplexer_server.select_one_channel('422')
freq_422 = b.multiplexer_server.get_frequency('422')

#if np.abs(freq_422 - 354.539170)*1e6 > 50:
if 1 == 2:
    
    print "The 422 nm frequency is wrong: " + str(freq_422) 
    print "Aborting loading procedure ..."
    
else:
            
    print "The 422 nm frequency is: " + str(freq_422)
    
    # what's missing
    # check frequency of 422
    # switch on oven
    # camera readout
    
    while counts < threshold: 

        # get PMT counts
        counts = cxn.normalpmtflow.get_next_counts('ON', 1, True)

        # switch off blue PI, if above threshold
        if counts > threshold:
            cxn.pulser.switch_manual('bluePI', False)
            print "Loaded an ion ..."

            time.sleep(0.5)

    
   

