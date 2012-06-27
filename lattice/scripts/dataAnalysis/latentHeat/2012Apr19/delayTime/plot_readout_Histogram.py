import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

totalTraces = 100
datasets = ['2012Apr12_2033_19','2012Apr12_2045_26','2012Apr12_2043_40','2012Apr12_2041_42',
              '2012Apr12_2039_40','2012Apr12_2037_26','2012Apr12_2034_49','2012Apr12_2030_05',
              '2012Apr12_2026_28','2012Apr12_2022_14']


refSigs = []
detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Histogram of readouts')

for datasetName in datasets:
    print 'Getting heating counts...'
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    xtal_record = dv.get_parameter('xtal_record')
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
        detectedCounts.append(countsReadout)
print 'Done'
pyplot.hist(detectedCounts, 60)
pyplot.show()