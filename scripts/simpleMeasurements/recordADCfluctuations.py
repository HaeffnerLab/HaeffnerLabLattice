import labrad
import time

#servers
cxn = labrad.connect()
dv = cxn.data_vault
adc = cxn.adcserver
ser = cxn.lab_197_serial_server

#global variables
CHANNEL = '3'
RESOLUTION = 1 # seconds
DURATION = 1
NUM_STEPS = DURATION / RESOLUTION
DEGREE_ROT = '01' #degrees

#set up data vault
dv.cd(['','QuickMeasurements','Power Fluctuations'],True)
dv.new('Power fluctuations {}'.format(CHANNEL),[('Time', 'sec')], [('Power','Volt','Volt')] )
dv.add_parameter('degree rotation', DEGREE_ROT)
dv.add_parameter('plotLive',True)
PORT = 'ttyUSB0'

ser.open(PORT,timeout = 1)
i = 0
while True: #for i in range(194): #this many 2 degree turns are required for a complete revolution
    print 'changing angle', i
    ser.write('01'+ DEGREE_ROT)
    for j in range(NUM_STEPS):
        voltage = adc.measurechannel(CHANNEL)
        angle = (i + float(j) / NUM_STEPS) * int(DEGREE_ROT)
        dv.add([angle,voltage])
        time.sleep(RESOLUTION)
    i += 1
print 'DONE'