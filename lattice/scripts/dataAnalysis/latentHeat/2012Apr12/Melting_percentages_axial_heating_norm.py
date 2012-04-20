import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

meltingThreshold = 600 
totalTraces = 50
datasets =  [['2012Apr12_2226_40','2012Apr12_2228_30'],['2012Apr12_2230_15','2012Apr12_2232_27',
             '2012Apr12_2235_45']]

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
title = 'melting'
pyplot.suptitle(title)

heat_times = []
percent_melt = []
refSigs = []

for datasetName in datasets[0]:
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
pyplot.xlim([10,50])
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