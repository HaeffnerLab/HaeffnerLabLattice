import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

meltingThreshold = 3000 
totalTraces = 100
datasets =  ['2012Mar20_0127_37', '2012Mar20_0117_49', '2012Mar20_0129_49',
            '2012Mar20_0132_28', '2012Mar20_0114_32']

            #['2012Mar20_0106_40', '2012Mar20_0058_12', '2012Mar20_0047_40', '2012Mar20_0103_49', 
            #'2012Mar20_0049_58', '2012Mar20_0054_17', '2012Mar20_0100_41', '2012Mar20_0109_44']#-3.5dBm

            #['2012Mar19_2316_52', '2012Mar19_2314_50', '2012Mar19_2307_11', '2012Mar19_2309_17',
            #'2012Mar19_2259_06', '2012Mar19_2311_56', '2012Mar19_2322_21', '2012Mar19_2318_46']#-2dBm
            #['2012Mar19_2231_27', '2012Mar19_2229_17', '2012Mar19_2233_22', '2012Mar19_2254_34',
            #'2012Mar19_2248_02', '2012Mar19_2235_54', '2012Mar19_2251_18']# 0dBm

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
title = 'RF = 2 dBm'
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
pyplot.xlabel('Scatter during heating (counts)')
pyplot.xlabel('Heating time (ms)')
pyplot.ylabel('Melted fraction')
pyplot.xlim([50,130])
pyplot.show()

fileObj = open(title + ".txt", "w")
times = str(heat_times).strip('[]')
fracs  = str(percent_melt).strip('[]')
fileObj.write(times)
fileObj.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
fileObj.write(fracs)
fileObj.close()

print 'DONE'

