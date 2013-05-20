import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot
import time

#info in the format, [(label, melting threshold, totalTraces, list of datasets),...]
info =[
       ('2012Jul20 no heat', 14000, 200 , ['{0}_{1:=04}_{2:=02}'.format('2012Jul20', x/100, x % 100) for x in [133710, 134819, 135948,141040, 142153, 143553, 145436]], '2012Jul20' ),
       ('2012Jul20 no heat', 5000, 200 , ['{0}_{1:=04}_{2:=02}'.format('2012Jul20', x/100, x % 100) for x in [152657]], '2012Jul20' ),
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
        dv.cd(['','Experiments','LatentHeat_Global_Auto',date,datasetName])
        dv.open(4)
        axial_heat = dv.get_parameter('axial_heat')
        readout_delay = dv.get_parameter('readout_delay')
        dv.open(2)    
        data = dv.get().asarray
        readout = data.transpose()[1]
        melted,above = getPercentage(readout, meltingThreshold)
        error_bars.append(errorBarSimple(totalTraces, melted))
        percent_melt.append(melted)
        delay_times.append(readout_delay)
    delay_times = 1000.0 * numpy.array(delay_times)
    percent_melt = numpy.array(percent_melt)
    error_bars = numpy.array(error_bars)
    print delay_times, percent_melt, error_bars
    delay_times, [percent_melt,error_bars] = arangeByFirst(delay_times, [percent_melt,error_bars])
    pyplot.errorbar(delay_times, percent_melt, fmt = '-o',  yerr = error_bars.transpose(), label = name)

pyplot.xlabel('Delay Time (ms)')
pyplot.ylabel('Melted fraction')
pyplot.legend()
pyplot.show()