import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot
import time

#info in the format, [(label, melting threshold, totalTraces, list of datasets),...]
info =[
       ('2012 June 27 delay time 5 ions, 8ms heat, compensated', 26000, 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [120005, 120403, 121531, 121901, 122148, 122418]]),
       ('2012 June 27 delay time 5 ions, 6.75ms heat, compensated', 26000, 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [123429, 123836, 124453, 125512]]),              
       ('2012 June 27 delay time 5 ions, 0ms heat, compensated', 26000, 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [130054]]),
       ('2012 June 27 delay time 5 ions, 8.35ms heat, compensated', 35000, 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [150959, 151424, 151724, 153048, 154120, 154614, 154946, 155305]]),
#       ('2012 June 27 delay time 5 ions, 7.5ms heat, endcapRF: 0 dBm', 35000, 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [160958, 161351, 161846, 162548]]),
#       ('2012 June 27 delay time 5 ions, 9.7ms heat, compensated for comparison', 35000, 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [163934, 164328, 165748]]),
#       ('2012 June 27 delay time 5 ions, 6.6ms heat, HV: 250V', 32000, 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [173905, 174250, 174854, 175825, 180340, 180653]]),
#       ('2012 June 27 delay time 5 ions, 6.9ms heat, endcapRF: 0 dBm', 20000, 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [182217, 182555, 182900, 183211]]),
#       ('2012 June 27 delay time 5 ions, slow heating 35.25ms', 17000 , 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [191421, 191803, 192407]]),
#       ('2012 June 27 delay time 5 ions, slow heating 31.25ms', 17000 , 85 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [193619, 194008, 194620]]),
#       ('2012 June 27 delay time 5 ions, outer ion heat 7.25ms', 20000 , 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [210543, 210919, 211257]]),
#       ('2012 June 27 delay time 5 ions, outer ion heat 6.1ms', 20000 , 200 , ['2012Jun27_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [212507, 212850, 213453, 214436, 214917]]),
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