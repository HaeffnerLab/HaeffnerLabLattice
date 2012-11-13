import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

meltingThreshold = 350
totalTraces = 100
datasets = ['2012Mar05_2021_19', '2012Mar05_2034_11','2012Mar05_2007_10']

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Different delay for 40ms heating, far red to discriminate')

delay_times = []
percent_melt = []

for datasetName in datasets:
    #getting parameters
    dv.cd(['','Experiments','LatentHeat_no729',datasetName])
    dv.open(1)    
    global_off_start =  dv.get_parameter('global_off_start')
    readout_delay = dv.get_parameter('readout_delay')
    heat_time = dv.get_parameter('axial_heat')
    delay_times.append(readout_delay / 10.**3)
    readout_delay = dv.get_parameter('readout_delay')
    shutter_delay = dv.get_parameter('shutter_delay')
    crystallize_delay = dv.get_parameter('crystallize_delay')
    recordTime = dv.get_parameter('recordTime')
    #readout range
    startReadout =  0.300
    stopReadout = 0.400
    print datasetName, startReadout, stopReadout
    #data processing on the fly
    dv.cd(['','Experiments','LatentHeat_no729',datasetName,'timetags'])
    melted = 0
    for dataset in range(1,totalTraces+1):
        #print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        if countsReadout > meltingThreshold: #for far red, melting means more counts
            melted +=1
    perc = melted / float(totalTraces)
    percent_melt.append(perc)

pyplot.plot(delay_times, percent_melt)
pyplot.xlabel('Heat Delay Time (ms)')
pyplot.show()