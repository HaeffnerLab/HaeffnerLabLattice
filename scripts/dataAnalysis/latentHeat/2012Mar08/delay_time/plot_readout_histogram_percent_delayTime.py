import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

meltingThreshold = 2350
totalTraces = 30
datasets = ['2012Mar08_1934_58', '2012Mar08_1935_44', '2012Mar08_1936_35', '2012Mar08_1937_38','2012Mar08_1938_36'] # 135 ms heating

#['2012Mar08_1928_29', '2012Mar08_1929_19', '2012Mar08_1930_00', '2012Mar08_1931_04','2012Mar08_1932_12'] # 95 ms heating
#['2012Mar08_1934_58', '2012Mar08_1935_44', '2012Mar08_1936_35', '2012Mar08_1937_38','2012Mar08_1938_36'] # 135 ms heating

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Melting percentage using readout beam: 95 ms Heating')

delay_times = []
percent_melt = []

for datasetName in datasets:
    #getting parameters
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    delay_times.append(readout_delay / 10.**3)
    readout_time = dv.get_parameter('readout_time')
   
    #readout range
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay ) / 10.0**6 #now in seconds
    stopReadout = startReadout + readout_time / 10.0**6 #now in seconds
    print datasetName, startReadout, stopReadout
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

print numpy.shape(delay_times)
pyplot.plot(delay_times, percent_melt, '-o')
pyplot.xlabel('Delay Time (ms)')
pyplot.ylabel('Melted fraction')
pyplot.ylim([0,1.0])
pyplot.show()