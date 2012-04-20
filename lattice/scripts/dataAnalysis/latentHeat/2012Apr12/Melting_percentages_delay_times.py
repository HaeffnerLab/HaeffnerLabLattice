import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

#meltingThreshold = 1000 
#totalTraces = 1
datasets =  [['2012Apr12_2158_28','2012Apr12_2202_27','2012Apr12_2159_18','2012Apr12_2200_41'],
             ['2012Apr12_2033_19','2012Apr12_2045_26','2012Apr12_2043_40','2012Apr12_2041_42',
              '2012Apr12_2039_40','2012Apr12_2037_26','2012Apr12_2034_49','2012Apr12_2030_05',
              '2012Apr12_2026_28','2012Apr12_2022_14'],
             ['2012Apr12_2223_45','2012Apr12_2221_05','2012Apr12_2218_11','2012Apr12_2215_22',
              '2012Apr12_2212_19','2012Apr12_2209_19','2012Apr12_2206_09'],
             ['2012Apr12_2150_53','2012Apr12_2152_43','2012Apr12_2154_32','2012Apr12_2156_30']]
             
             #['2012Apr12_2033_19','2012Apr12_2045_26','2012Apr12_2043_40','2012Apr12_2041_42',
             # '2012Apr12_2039_40','2012Apr12_2037_26','2012Apr12_2034_49','2012Apr12_2030_05',
             # '2012Apr12_2026_28','2012Apr12_2022_14']

detectedCounts = [] #list of counts detected during readout

fig, ax = pyplot.subplots()
fig.clf()
title = ''
#pyplot.suptitle(title)


refSigs = []

for x in range(len(datasets)):
    if x == 1:
        totalTraces = 100
        meltingThreshold = 1000 
    else:
        totalTraces = 50
        meltingThreshold = 600
    delay_times = []
    percent_melt = []
    print x
    for datasetName in datasets[x]:
        refs = 0
        #getting parameters
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
        dv.open(1)    
        initial_cooling = dv.get_parameter('initial_cooling')
        heat_delay = dv.get_parameter('heat_delay')
        axial_heat = dv.get_parameter('axial_heat')
        readout_delay = dv.get_parameter('readout_delay')
        delay_times.append(readout_delay * 10.**3)
        #readout_delay = dv.get_parameter('readout_delay')
        readout_time = dv.get_parameter('readout_time')
        xtal_record = dv.get_parameter('xtal_record')
       
        #readout range
        heatStart = (initial_cooling + heat_delay ) #in seconds
        heatEnd = (initial_cooling + heat_delay +axial_heat ) #in seconds
        startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay )  #in seconds
        stopReadout = startReadout + readout_time # in seconds
        print datasetName#, startReadout, stopReadout, heatStart, heatEnd
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
        #print refs
        refs = refs/30
        refSigs.append(refs)
        perc = melted / float(totalTraces)
        percent_melt.append(perc)
    
    numpy.set_printoptions(precision=2)
    g = numpy.array(delay_times)
    print 'delay times = ',g
    print 'melted fraction =',percent_melt
    
    pyplot.plot(g, percent_melt, '-o', label = 'Heating time {0} ms'.format(axial_heat*1e3))
    pyplot.hold('True')
    
#ax.set_xscale('log')
pyplot.xlabel('Delay time (ms)')
pyplot.ylabel('Melted fraction')
pyplot.legend()
pyplot.xlim([0,1050])
pyplot.ylim([-0.05,1.05])
pyplot.show()

#fileObj = open(title + ".txt", "w")
#times = str(delay_times).strip('[]')
#fracs  = str(percent_melt).strip('[]')
#fileObj.write(times)
#fileObj.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
#fileObj.write(fracs)
#fileObj.close()

print 'DONE'

#figure = pyplot.figure()
#figure.clf
#pyplot.plot(heat_times, refSigs, '-o')
#pyplot.xlabel('Heating time (ms)')
#pyplot.ylabel('Heating fluorescence')
#pyplot.show()