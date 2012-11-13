import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot


totalTraces = 30
datasets = ['2012Mar08_1918_28', '2012Mar08_1920_06','2012Mar08_1922_59','2012Mar08_1919_12',
            '2012Mar08_1921_47','2012Mar08_1920_53','2012Mar08_1924_11','2012Mar08_1926_43']

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle(datasets[0])
for datasetName in datasets:
    #getting parameters
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    
    #readout range
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay ) / 10.0**6 #now in seconds
    stopReadout = startReadout + readout_time / 10.0**6 #now in seconds
    print datasetName, startReadout, stopReadout
    #data processing on the fly
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
    for dataset in range(1,totalTraces+1):
        #print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        detectedCounts.append(countsReadout)

pyplot.hist(detectedCounts, 60)
pyplot.show()