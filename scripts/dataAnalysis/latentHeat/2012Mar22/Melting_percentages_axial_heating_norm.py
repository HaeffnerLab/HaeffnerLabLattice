import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

meltingThreshold = 4000 
totalTraces = 10
datasets =  ['2012Mar22_2031_19']#,'2012Mar22_2043_29','2012Mar22_2037_07','2012Mar22_2040_07','2012Mar22_2033_40']#-30V
            #['2012Mar22_2028_56','2012Mar22_2020_39','2012Mar22_2026_20','2012Mar22_2017_29','2012Mar22_2022_56']#-15V
            #['2012Mar22_2008_31','2012Mar22_1958_28','2012Mar22_2014_37','2012Mar22_2001_20','2012Mar22_2011_12']#0V
            #['2012Mar22_1951_55','2012Mar22_1946_14','2012Mar22_1939_50','2012Mar22_1948_33','2012Mar22_1942_40']#15V
            #['2012Mar22_1915_06','2012Mar22_1925_02','2012Mar22_1927_47','2012Mar22_1921_04','2012Mar22_1917_31']#30V

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
title = 'Compensation Tilt = -30 V'
pyplot.suptitle(title)

heat_times = []
percent_melt = []
refSigs = []

for datasetName in datasets:
    refs = 0
    #getting parameters
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    heat_times.append(axial_heat * 10.**3)
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    xtal_record = dv.get_parameter('xtal_record')
   
    #readout range
    heatStart = (initial_cooling + heat_delay ) #in seconds
    heatEnd = (initial_cooling + heat_delay +axial_heat ) #in seconds
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay )  #in seconds
    stopReadout = startReadout + readout_time # in seconds
    print datasetName, startReadout, stopReadout, heatStart, heatEnd
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
    melted = 0
    for dataset in range(1,totalTraces+1):
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        refReadout = numpy.count_nonzero((heatStart <= timetags) * (timetags <= heatEnd))
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        if countsReadout < meltingThreshold: # melting is less counts
            melted +=1
        refs = refs + refReadout    
        #refs.append(refReadout)
    print refs
    refs = refs/30
    refSigs.append(refs)
    perc = melted / float(totalTraces)
    percent_melt.append(perc)

numpy.set_printoptions(precision=2)
print percent_melt
g = numpy.array(heat_times)
print g, refSigs 

pyplot.plot(heat_times, percent_melt, '-o')
pyplot.xlabel('Heating time (ms)')
pyplot.ylabel('Melted fraction')
#pyplot.legend()
pyplot.xlim([20,70])
pyplot.show()

fileObj = open(title + ".txt", "w")
times = str(heat_times).strip('[]')
fracs  = str(percent_melt).strip('[]')
fileObj.write(times)
fileObj.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
fileObj.write(fracs)
fileObj.close()

print 'DONE'

#figure = pyplot.figure()
#figure.clf
#pyplot.plot(heat_times, refSigs, '-o')
#pyplot.xlabel('Heating time (ms)')
#pyplot.ylabel('Heating fluorescence')
#pyplot.show()