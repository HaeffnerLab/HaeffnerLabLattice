import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

#info in the format, [(label, melting threshold, totalTraces, list of datasets),...]
info =[
       ('10ions RF -3.5dBm', 225, 50, ['2012Apr19_1636_17','2012Apr19_1639_12','2012Apr19_1637_26','2012Apr19_1640_40','2012Apr19_1643_10','2012Apr19_1645_06']),
       ('10ions RF -4.2dBm', 187, 50, ['2012Apr19_1709_12','2012Apr19_1710_14','2012Apr19_1712_08','2012Apr19_1713_19','2012Apr19_1717_32']),
       ('10ions RF -5.0dBm', 200, 50, ['2012Apr19_1749_14','2012Apr19_1750_24','2012Apr19_1751_39','2012Apr19_1753_24','2012Apr19_1754_39','2012Apr19_1756_20']),
       ('10ions RF -7.0dBm (close to zigzag)', 180, 50, ['2012Apr19_1812_35','2012Apr19_1811_24','2012Apr19_1813_37','2012Apr19_1814_42','2012Apr19_1815_43']),
       ('15ions RF -3.5dBm', 250, 50, ['2012Apr19_1935_17', '2012Apr19_1937_28','2012Apr19_1939_32', '2012Apr19_1940_47','2012Apr19_1942_22']),
       ('15ions RF -7.0dBm, zigzag', 250, 50, ['2012Apr19_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [203455,203604,203812,203942,204211]]),
       ] 

#make figure
figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Melting percentage during heating, no delay')

for i in range(len(info)):
    label = info[i][0]
    meltingThreshold = info[i][1]
    totalTraces = info[i][2]
    datasets = info[i][3]
    heat_times = []
    percent_melt = []
    for datasetName in datasets:
        print datasetName
        #getting parameters
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
        dv.open(1)    
        initial_cooling = dv.get_parameter('initial_cooling')
        heat_delay = dv.get_parameter('heat_delay')
        axial_heat = dv.get_parameter('axial_heat')
        axial_heat = dv.get_parameter('axial_heat')
        readout_delay = dv.get_parameter('readout_delay')
        readout_time = dv.get_parameter('readout_time')
        heat_times.append(axial_heat)
        #heatRange
        startHeat = initial_cooling + heat_delay
        endHeat = startHeat + startHeat
        #readout range
        startReadout =  endHeat + readout_delay
        stopReadout = startReadout + readout_time 
        #data processing on the fly
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
        melted = 0
        for dataset in range(1,totalTraces+1):
            #print dataset
            dv.open(int(dataset))
            timetags = dv.get().asarray[:,0]
            countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
            if countsReadout < meltingThreshold: # melting is less counts
                melted +=1
        perc = melted / float(totalTraces)
        percent_melt.append(perc)
    pyplot.plot(heat_times, percent_melt, 'o', label = label)
    pyplot.hold('True')

pyplot.xlabel('Heating Time (ms)')
pyplot.ylabel('Melted fraction')
pyplot.legend()
pyplot.show()