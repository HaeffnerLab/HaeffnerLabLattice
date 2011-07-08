adapter = 0;
charsfromendinpacket = 4;
signfromendinpacket = 5;
signforopenshutter = '+';
signforclosedshutter = '-';
numtocollect = 2;
sentinelnopack = -1;
dir = ['','FirstTrapping'];
import labrad
import time

cxn = labrad.connect('localhost')


dvault = cxn.data_vault
dvault.cd(dir,True)
dvault.new('PMTcounts', [('t', 'num')], [('KiloCounts/sec','Open Shutter','num'),('KiloCounts/sec','Closed Shutter','num'),('KiloCounts/sec','Differential Signal','num')])

count = 0;
data = [[]]*numtocollect
opencounts = 0; #initial values for the counts
closedcounts = 0;
while (count < 100000000):
        data = [float(count),float(count),float(count),float(count)]
        count = count + 1;
    #print data
        dvault.add(data)

