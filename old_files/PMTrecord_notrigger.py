adapter = 0;
charsfromendinpacket = 4;
numtocollect = 2;
sentinelnopack = -1;
dir = ['','FirstTrapping'];
import labrad
import time


cxn = labrad.connect('localhost')
eth = cxn._direct_ethernet
eth.Connect(adapter)
eth.timeout(1)#sets timeout to 1 DAY, how long collect function waits before it returns error
eth.Listen()


dvault = cxn.data_vault
dvault.cd(dir,True)
dvault.new('PMTcounts', [('t', 'num')], [('totalCounts','','num')])
eth.clear()
time.sleep(1)

count = 0;
data = [[]]*numtocollect
while (count < 1000000):
    fut = eth.Collect(numtocollect,wait=False)
    fut.wait()
    packet = eth.Read(numtocollect);
    for i in range(numtocollect):
        message = packet[i][3]; 
        readout = message[-charsfromendinpacket:];
        if(readout.isdigit()):
        #print float(readout)
            data[i] = [float(count),float(readout)]
        #else:
        #    data[i] = [sentinelnopack,sentinelnopack];
    dvault.add(data)
    count = count + 1;
