import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

totalTraces = 50
datasets = ['2012Apr19_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [203455,203604,203812,203942,204211]]

#['2012Apr19_1935_17', '2012Apr19_1937_28','2012Apr19_1939_32', '2012Apr19_1940_47','2012Apr19_1942_22'] 
#['2012Apr19_1812_35','2012Apr19_1811_24','2012Apr19_1813_37','2012Apr19_1814_42','2012Apr19_1815_43']
#['2012Apr19_1749_14','2012Apr19_1750_24','2012Apr19_1751_39','2012Apr19_1753_24','2012Apr19_1754_39','2012Apr19_1756_20']
#['2012Apr19_1709_12','2012Apr19_1710_14','2012Apr19_1712_08','2012Apr19_1713_19','2012Apr19_1717_32']
#['2012Apr19_1636_17','2012Apr19_1639_12','2012Apr19_1637_26','2012Apr19_1640_40','2012Apr19_1643_10','2012Apr19_1645_06']


refSigs = []
detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Histogram of readouts')

for datasetName in datasets:
    print 'Getting heating counts...'
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    print dv.dir()
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    xtal_record = dv.get_parameter('xtal_record')
#    
    # readout range
    heatStart = (initial_cooling + heat_delay ) # / 10.0**6 #in seconds
    heatEnd = (initial_cooling + heat_delay +axial_heat ) 
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay ) 
    stopReadout = startReadout + readout_time 
    print datasetName, heatStart, heatEnd, startReadout, stopReadout
    print 'Heating time :', heatEnd - heatStart
    print 'Delay time :', readout_delay
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
        
    for dataset in range(1,totalTraces+1):
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        #normCounts = (float(refReadout) / float(max(refSigs))) * (countsReadout)  
        detectedCounts.append(countsReadout)
print 'Done'
pyplot.hist(detectedCounts, 60)
pyplot.show()