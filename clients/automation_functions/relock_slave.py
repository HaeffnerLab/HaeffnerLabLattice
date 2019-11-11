import labrad
import time
import numpy as np
import os

# connect to local labrad
cxn = labrad.connect()

# connect to labrad in laserroom
b = labrad.connect('192.168.169.49')

# checking frequency of 729 injection lock
lst = b.multiplexer_server.get_available_channels()



fault_counter = 0
while True:

   ch_settings = []
   for ch in lst:
       ch_settings.append(b.multiplexer_server.get_state(ch))

   # get current master frequency
   b.multiplexer_server.select_one_channel('729')   
   time.sleep(1.0)
   master_freq_729 = b.multiplexer_server.get_frequency('729')

   # get current injection lock frequency
   b.multiplexer_server.select_one_channel('729 inject')   
   time.sleep(1.0)

   freq_422 = b.multiplexer_server.get_frequency('729 inject')
   print "Current frequencies inject diode/master: " + str(freq_422) + " / " + str(master_freq_729)

   for k in range(len(lst)):
       b.multiplexer_server.set_state(lst[k], ch_settings[k])   

   time.sleep(10)

	
   
   

