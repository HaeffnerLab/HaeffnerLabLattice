import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import time

totalTraces = 200

title = 'no heat' ; datasets = ['2012Jun28_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [214645, 215101, 215658, 220624, 221918, 223542]]

def arangeByParameter(datasets, parameter):
    parList = []
    for dataset in datasets:
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',dataset])
        dv.open(1)
        par = float(dv.get_parameter(parameter))
        parList.append(par)
    together = zip(datasets, parList)
    s = sorted(together, key = lambda x: x[1])
    s = list(zip(*s)[0])
    return s

datasets = arangeByParameter(datasets, 'readout_delay')

refSigs = []
detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()

figure.clf()
pyplot.suptitle('Histogram of readouts')
colormap = pyplot.cm.gist_ncar
ax = pyplot.axes()
ax.set_color_cycle([colormap(i) for i in numpy.linspace(0, 0.9, len(datasets))])

for datasetName in datasets:
    print 'Getting timetags...{}'.format(datasetName)
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    datasetCounts = []
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
    startReadout =  (axial_heat + initial_cooling + heat_delay + axial_heat + readout_delay ) 
    stopReadout = startReadout + readout_time 
    print datasetName, heatStart, heatEnd, startReadout, stopReadout
    print 'Heating time :', heatEnd - heatStart
    print 'Delay time :', readout_delay
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
        
    for dataset in range(1,totalTraces+1):
        print dataset
        print 'pausing!'
        time.sleep(0.1)
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        countsReadout = countsReadout / float(readout_time) #now in counts/secz
        datasetCounts.append(countsReadout)
        detectedCounts.append(countsReadout)
    pyplot.hist(datasetCounts, 60, histtype = 'step', label = 'heating = {0} ms, delay = {1} ms'.format(1000 * axial_heat, 1000 * readout_delay))

print 'Done'
pyplot.hist(detectedCounts, 60, histtype = 'step', label = 'Total', color = 'black')
pyplot.xlabel('Counts / Sec')
pyplot.title(title)
pyplot.legend()
pyplot.show()