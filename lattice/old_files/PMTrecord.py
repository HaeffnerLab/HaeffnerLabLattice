adapter = 1;
charsfromendinpacket = 4;
signfromendinpacket = 5;
signforopenshutter = '+';
signforclosedshutter = '-';
numtocollect = 2;
sentinelnopack = -1;
dir = ['','SecondTrapping'];

import labrad
import time

cxn = labrad.connect()
eth = cxn._direct_ethernet
eth.Connect(adapter)
eth.timeout(1)#sets timeout to 1 DAY, how long collect function waits before it returns error
eth.Listen()

dvault = cxn.data_vault
dvault.cd(dir,True)
floatname = dvault.new('PMTcounts', [('t', 'num')], [('KiloCounts/sec','Open Shutter','num'),('KiloCounts/sec','Closed Shutter','num'),('KiloCounts/sec','Differential Signal','num')])
eth.clear()
time.sleep(1)
        
count = 0;
data = [[]]*numtocollect
opencounts = 0; #initial values for the counts
closedcounts = 0;
while (count < 100000000):
    fut = eth.Collect(numtocollect,wait=False)
    fut.wait()
    packet = eth.Read(numtocollect);
    for i in range(numtocollect):
        message = packet[i][3]; 
        readout = message[-charsfromendinpacket:];
        sign = message[-signfromendinpacket:-charsfromendinpacket];
        if(readout.isdigit()): #packet is a number, seems not malformed
            #print 'recording'
            #print float(count)
            #print float(readout)
            #print str(sign)
            if(str(sign) == signforopenshutter):
                opencounts = readout
            elif (str(sign) == signforclosedshutter):
                closedcounts = readout
        differential = float(opencounts) - float(closedcounts)
        data[i] = [float(count),float(opencounts),float(closedcounts),float(differential)]
        count = count + 1;
    #print data
    dvault.add(data)

