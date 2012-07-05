import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

#info in the format, [(label, melting threshold, totalTraces, list of datasets),...]
info =[
       ('2012Jul03 no heat', 30000, 200, ['{0}_{1:=04}_{2:=02}'.format('2012Jul03', x/100, x % 100) for x in [211021, 211322, 211916, 212831]], '2012Jul03' ),
       ('2012Jul04 no heat', 30000, 200,  ['{0}_{1:=04}_{2:=02}'.format('2012Jul04', x/100, x % 100) for x in [82928, 85057, 91856]], '2012Jul04' ),
       ] 
#make figure
figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Binned Separated')

class Binner():
    '''Helper class for binning received timetags'''
    def __init__(self, totalWidth, binWidth):
        self.averaged = 0
        self.binWidth = binWidth
        binNumber = int(totalWidth / binWidth)
        self.binArray = binWidth * numpy.arange(binNumber + 1)
        self.binned = numpy.zeros(binNumber)
    
    def add(self, newData, added = 1):
        newbinned = numpy.histogram(newData, self.binArray )[0]
        self.binned += newbinned
        self.averaged += added
    
    def howManyAdded(self):
        return self.averaged
    
    def getBinned(self, normalize = True):
        if normalize:
            try:
                self.binned = self.binned / self.averaged
                self.binned = self.binned / self.binWidth
            except FloatingPointError:
                raise Exception ("BINNER: Can't normalize since no data has been added")
        return (self.binArray[0:-1], self.binned)

for i in range(len(info)):
    name = info[i][0]
    meltingThreshold = info[i][1]
    datasets = info[i][3]
    date = info[i][4]
    for datasetName in datasets:
        print datasetName
        dv.cd(['','Experiments','LatentHeat_Global_Auto',date,datasetName])
        dv.open(4)
        axial_heat = dv.get_parameter('axial_heat')
        readout_delay = dv.get_parameter('readout_delay')
        start_readout = dv.get_parameter('startReadout')
        end_readout = dv.get_parameter('endReadout')
        record_time = dv.get_parameter('recordTime')
        meltedBinned = Binner(record_time, 500e-6)
        xtalBinned = Binner(record_time, 500e-6)
        totalBinned = Binner(record_time, 500e-6)
        dv.open(1)
        data = dv.get().asarray
        iterations = data[:,0]
        timetags = data[:,1]
        iters,indices = numpy.unique(iterations, return_index=True) #finds the iterations, and positions of new iterations beginning
        split = numpy.split(timetags, indices[1:]) #timetags are split for each iteration
        for enum,tags in enumerate(split):
            counts = numpy.count_nonzero( (tags >= start_readout) * (tags <= end_readout) )
            counts = counts / (end_readout - start_readout)
            totalBinned.add(tags)
            if counts <= meltingThreshold:
                meltedBinned.add(tags)
            else:
                xtalBinned.add(tags)
        t,xtal = xtalBinned.getBinned()
        t,melted = meltedBinned.getBinned()
        #t,total = totalBinned.getBinned()
        pyplot.plot(t * 1000, xtal, label = 'crystallized {}'.format(datasetName))
        pyplot.plot(t * 1000, melted, label = 'melted {}'.format(datasetName))
        #pyplot.plot(t * 1000, total, label = 'total {}'.format(datasetName))
        
pyplot.xlabel('Time (ms)')
pyplot.ylabel('Fluor Counts/Sec')
pyplot.legend()
pyplot.show()