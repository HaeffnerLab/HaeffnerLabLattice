import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import time

#info in the format, [(label, melting threshold, totalTraces, list of datasets),...]
info =[
       ('2012Jun28 no heat', 40000, 200 , ['2012Jun28_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [214645, 215101, 215658, 220624, 221918, 223542]]),
       ] 

#make figure
figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Equilibration')


def errorBarSimple(trials, prob):
    #look at wiki http://en.wikipedia.org/wiki/Checking_whether_a_coin_is_fair
    '''returns 1 sigma error bar'''
    Z = 1.0
    s = numpy.sqrt(prob * (1.0 - prob) / float(trials))
    err = Z * s
    return (err,err)

def arangeByFirst(one,rest):
    '''given n arrays, returns them sorted in the order of the increasing first array'''
    tosort = one.argsort()
    sortedArrs = []
    one = one[tosort]
    for arr in rest:
        sortedArrs.append(arr[tosort])
    return one,sortedArrs

for i in range(len(info)):
    name = info[i][0]
    meltingThreshold = info[i][1]
    totalTraces = info[i][2]
    datasets = info[i][3]
    delay_times = []
    percent_melt = []
    error_bars = []
    for datasetName in datasets:
        print datasetName
        print 'pausing!'; time.sleep(30)
        #getting parameters
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
        dv.open(1)    
        initial_cooling = dv.get_parameter('initial_cooling')
        heat_delay = dv.get_parameter('heat_delay')
        axial_heat = dv.get_parameter('axial_heat')
        readout_delay = dv.get_parameter('readout_delay')
        readout_time = dv.get_parameter('readout_time')
        delay_times.append(readout_delay)
        #heatRange
        #readout range
        startReadout =  (axial_heat + initial_cooling + heat_delay + axial_heat + readout_delay ) 
        stopReadout = startReadout + readout_time 
        #data processing on the fly
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
        melted = 0
        for dataset in range(1,totalTraces+1):
            #print dataset
            dv.open(int(dataset))
            timetags = dv.get().asarray[:,0]
            countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
            countsReadout = countsReadout / float(readout_time) #now in counts/sec
            if countsReadout < meltingThreshold: # melting is less counts
                melted +=1
        perc = melted / float(totalTraces)
        error_bars.append(errorBarSimple(totalTraces, perc))
        percent_melt.append(perc)
    delay_times = 1000.0 * numpy.array(delay_times)
    percent_melt = numpy.array(percent_melt)
    error_bars = numpy.array(error_bars)
    delay_times, [percent_melt,error_bars] = arangeByFirst(delay_times, [percent_melt,error_bars])
    pyplot.errorbar(delay_times, percent_melt, fmt = '-o',  yerr = error_bars.transpose(), label = name)

pyplot.xlabel('Delay Time (ms)')
pyplot.ylabel('Melted fraction')
pyplot.legend()
pyplot.show()