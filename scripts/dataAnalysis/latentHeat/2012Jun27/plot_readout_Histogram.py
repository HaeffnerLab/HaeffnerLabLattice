import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import time

totalTraces = 200

#title = '2012 June 27 delay time 5 ions, 8ms heat, compensated' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [120005, 120403, 121531, 121901, 122148, 122418]]
#title = '2012 June 27 delay time 5 ions, 6.75ms heat, compensated' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [123429, 123836, 124453, 125512]]
#title = '2012 June 27 delay time 5 ions, 0ms heat, compensated' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [130054]]
#title = '2012 June 27 delay time 5 ions, 8.35ms heat, compensated' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [150959, 151424, 151724, 153048, 154120, 154614, 154946, 155305]]
#title = '2012 June 27 delay time 5 ions, 7.5ms heat, endcapRF: 0 dBm' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [160958, 161351, 161846, 162548]]
#title = '2012 June 27 delay time 5 ions, 9.7ms heat, compensated for comparison' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [163934, 164328, 165748]]
#title = '2012 June 27 delay time 5 ions, 6.6ms heat, HV: 250V' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [173905, 174250, 174854, 175825, 180340, 180653]]
#title = '2012 June 27 delay time 5 ions, 6.9ms heat, endcapRF: 0 dBm' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [182217, 182555, 182900, 183211]]
#title = '2012 June 27 delay time 5 ions, slow heating 35.25ms' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [191421, 191803, 192407]]
#title = '2012 June 27 delay time 5 ions, slow heating 31.25ms' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [193619, 194008, 194620]]
#title = '2012 June 27 delay time 5 ions, outer ion heat 7.25ms' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [210543, 210919, 211257]]
title = '2012 June 27 delay time 5 ions, outer ion heat 6.1ms' ; datasets = ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [212507, 212850, 213453, 214436, 214917]]

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