import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

totalTraces = 200

#title = '2012 June 21 delay time 5 ions' ; datasets = ['2012Jun21_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [192851,193305,193518,193826, 194101,194327,194601,194925,200802, 201806]] #heating time'
#title = '2012 June 21 delay time 10 ions' ; datasets = ['2012Jun21_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [204347,204755, 205035, 205356, 205735, 210012, 210252, 210519, 210742, 211338]]
#title = '2012 June 21 delay time 15 ions' ; datasets = ['2012Jun21_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [213349, 213806, 214046, 214446, 214913, 215238, 215610, 215848, 223117, 223533, 223852, 224508]]
#title = '2012 June 21 delay time 19 ions' ; datasets = ['2012Jun21_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [231600, 232030, 232357, 232707, 233111, 233359, 234121]]
title = '2012 June 21 delay time 2 ions';  datasets = ['2012Jun22_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [1335, 1743, 2050, 2314, 3047, 2550, 3417, 3946, 2824, 5047]]

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