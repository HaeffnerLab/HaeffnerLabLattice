import time
import numpy

def swtichXtalON(slptime):
    from lrexp.lr import Client
    dp = Client.connection.rohdeschwarz_server
    dp.select_device('lattice-pc GPIB Bus - USB0::0x0AAD::0x0054::104542')
    if not dp.output(): print 'WARNING crystallization beam is already on'
    print 'switching on crystallization beam'
    dp.output(False) #xtal beam is the 0th order, so turning off double pass enhances it
    time.sleep(slptime)
    dp.output(True)
    print 'switching off'