import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot


totalTraces = 100
datasets = ['2012Mar05_2021_19', '2012Mar05_2034_11','2012Mar05_2007_10']

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('histogram of detected counts')
for datasetName in datasets:
    #getting parameters
    dv.cd(['','Experiments','LatentHeat_no729',datasetName])
    dv.open(1)    
    global_off_start =  dv.get_parameter('global_off_start')
    heat_delay = dv.get_parameter('heat_delay')
    heat_time = dv.get_parameter('axial_heat')
    heat_time_ms = heat_time / 10**3
    readout_delay = dv.get_parameter('readout_delay')
    shutter_delay = dv.get_parameter('shutter_delay')
    crystallize_delay = dv.get_parameter('crystallize_delay')
    #readout range
    startReadout =  (global_off_start + heat_delay + heat_time + readout_delay ) / 10.0**6 #now in seconds
    stopReadout = startReadout + (shutter_delay + crystallize_delay) / 10.0**6 #now in seconds
    print datasetName, startReadout, stopReadout
    #data processing on the fly
    dv.cd(['','Experiments','LatentHeat_no729',datasetName,'timetags'])
    for dataset in range(1,totalTraces+1):
        #print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        detectedCounts.append(countsReadout)

pyplot.hist(detectedCounts, 60)
pyplot.show()