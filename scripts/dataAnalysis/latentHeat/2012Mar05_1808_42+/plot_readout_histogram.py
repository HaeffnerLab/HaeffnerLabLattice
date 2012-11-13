import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot


totalTraces = 100
datasets = ['2012Mar05_1808_42', '2012Mar05_1814_52', '2012Mar05_1828_23', '2012Mar05_1834_31']

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('histogram of detected counts')
for datasetName in datasets:
    #getting parameters
    dv.cd(['','Experiments','LatentHeat_no729',datasetName])
    dv.open(1)    
    global_off_start =  dv.get_parameter('global_off_start')
    global_off_time = dv.get_parameter('global_off_time')
    shutter_delay = dv.get_parameter('shutter_delay')
    crystallize_delay = dv.get_parameter('crystallize_delay')
    #readout range
    startReadout =  (global_off_start + global_off_time) / 10.0**6 #now in seconds
    stopReadout = startReadout + (shutter_delay + crystallize_delay) / 10.0**6 #now in seconds
    #data processing on the fly
    dv.cd(['','Experiments','LatentHeat_no729',datasetName,'timetags'])
    for dataset in range(1,totalTraces+1):
        print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        detectedCounts.append(countsReadout)

pyplot.hist(detectedCounts, 20)
pyplot.show()