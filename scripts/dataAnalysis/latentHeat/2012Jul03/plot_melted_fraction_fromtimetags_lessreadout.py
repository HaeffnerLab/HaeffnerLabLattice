import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot
import time

READOUT = 100e-6
#info in the format, [(label, melting threshold, totalTraces, list of datasets),...]
info =[
       ('2012Jul03 no heat', 15000, 200 , ['{0}_{1:=04}_{2:=02}'.format('2012Jul03', x/100, x % 100) for x in [211021, 211322, 211916, 212831]], '2012Jul03' ),
       ('2012Jul04 no heat', 15000, 200 , ['{0}_{1:=04}_{2:=02}'.format('2012Jul04', x/100, x % 100) for x in [82928, 85057, 91856]], '2012Jul04' ),
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

def getPercentage(counts, threshold):
    below = numpy.count_nonzero(counts <= threshold) / float(counts.size)
    above = numpy.count_nonzero(counts > threshold) / float(counts.size)
    return (below, above)

for i in range(len(info)):
    name = info[i][0]
    meltingThreshold = info[i][1]
    totalTraces = info[i][2]
    datasets = info[i][3]
    date = info[i][4]
    delay_times = []
    percent_melt = []
    error_bars = []
    for datasetName in datasets:
        print datasetName
        dv.cd(['','Experiments','LatentHeat_Global_Auto',date,datasetName])
        dv.open(4)
        axial_heat = dv.get_parameter('axial_heat')
        readout_delay = dv.get_parameter('readout_delay')
        start_readout = dv.get_parameter('startReadout')
        end_readout = READOUT + start_readout
        dv.open(1)
        data = dv.get().asarray
        iterations = data[:,0]
        timetags = data[:,1]
        iters,indices = numpy.unique(iterations, return_index=True) #finds the iterations, and positions of new iterations beginning
        split = numpy.split(timetags, indices[1:]) #timetags are split for each iteration
        readout = []
        for tags in split:
            counts = numpy.count_nonzero( (tags >= start_readout) * (tags <= end_readout) )
            counts = counts / (end_readout - start_readout)
            readout.append(counts)
        readout = numpy.array(readout)
        melted,above = getPercentage(readout, meltingThreshold)
        error_bars.append(errorBarSimple(totalTraces, melted))
        percent_melt.append(melted)
        delay_times.append(readout_delay)
    delay_times = 1000.0 * numpy.array(delay_times)
    percent_melt = numpy.array(percent_melt)
    error_bars = numpy.array(error_bars)
    delay_times, [percent_melt,error_bars] = arangeByFirst(delay_times, [percent_melt,error_bars])
    pyplot.errorbar(delay_times, percent_melt, fmt = '-o',  yerr = error_bars.transpose(), label = name)

pyplot.xlabel('Delay Time (ms)')
pyplot.ylabel('Melted fraction')
pyplot.legend()
pyplot.show()