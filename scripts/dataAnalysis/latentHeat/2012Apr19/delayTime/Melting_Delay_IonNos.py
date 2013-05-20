import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

meltingThreshold = 100 
totalTraces = 1
datasets =   [['2012Apr12_2033_19','2012Apr12_2045_26','2012Apr12_2043_40','2012Apr12_2041_42',
              '2012Apr12_2039_40','2012Apr12_2037_26','2012Apr12_2034_49','2012Apr12_2030_05',
              '2012Apr12_2026_28','2012Apr12_2022_14'],  # 5 ions
              ]
#              ['2012Apr19_1647_06','2012Apr19_1648_25','2012Apr19_1649_33','2012Apr19_1651_16',
#               '2012Apr19_1653_11', '2012Apr19_1655_13','2012Apr19_1657_09','2012Apr19_1659_25','2012Apr19_1702_19'], #10
#              ['2012Apr19_1944_39','2012Apr19_1956_00','2012Apr19_1954_34','2012Apr19_1647_06','2012Apr19_1945_56',
#               '2012Apr19_1947_48','2012Apr19_1950_02','2012Apr19_1951_54'], # 15
#               ['2012Apr19_2043_39','2012Apr19_2051_40','2012Apr19_2053_11','2012Apr19_2044_45',
#                '2012Apr19_2046_42','2012Apr19_2054_46','2012Apr19_2048_54'] ] #15 zigzag 
            
detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
title = 'Varying delay at different ion numbers'
pyplot.suptitle(title)

heat_times = []
delay_times = []
percent_melt = []
refSigs = []

for x in range(len(datasets)):
    if x == 0:
        meltingThreshold = 1000 
        totalTraces = 100
    elif x == 1:
        meltingThreshold = 180 
        totalTraces = 50
    elif x==2:
        meltingThreshold = 250
        totalTraces = 50
    elif x==3:
        meltingThreshold = 240
        totalTraces = 50
    delay_times = []
    percent_melt = []
    for datasetName in datasets[x]:
        refs = 0
        #getting parameters
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
        print  'threshold', meltingThreshold
        print 'totlal traces', totalTraces
        dv.open(1)    
        initial_cooling = dv.get_parameter('initial_cooling')
        heat_delay = dv.get_parameter('heat_delay')
        axial_heat = dv.get_parameter('axial_heat')
        heat_times.append(axial_heat * 10.**3)
        readout_delay = dv.get_parameter('readout_delay')
        delay_times.append(readout_delay * 10.**3)
        axial_heat = dv.get_parameter('axial_heat')
        readout_delay = dv.get_parameter('readout_delay')
        readout_time = dv.get_parameter('readout_time')
        xtal_record = dv.get_parameter('xtal_record')
        rf_power = dv.get_parameter('rf_power')
       
        #readout range
        heatStart = (initial_cooling + heat_delay ) #in seconds
        heatEnd = (initial_cooling + heat_delay +axial_heat ) #in seconds
        startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay )  #in seconds
        stopReadout = startReadout + readout_time # in seconds
        print datasetName#, startReadout, stopReadout, heatStart, heatEnd
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
        melted = 0
        print startReadout
        print stopReadout
        for dataset in range(1,totalTraces+1):
            dv.open(int(dataset))
            timetags = dv.get().asarray[:,0]
            refReadout = numpy.count_nonzero((heatStart <= timetags) * (timetags <= heatEnd))
            countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
            if countsReadout < meltingThreshold: # melting is less counts
                melted +=1
            refs = refs + refReadout    
            refs = refs/totalTraces
        refSigs.append(refs)
        perc = melted / float(totalTraces)
        percent_melt.append(perc)
        print 'Heating time :', heatEnd - heatStart
        print 'Delay time :', readout_delay
        print 'Melted = {0} %'.format(100*perc)
    pyplot.plot(delay_times, percent_melt, '-o', label = 'RF = {0} dBm'.format(meltingThreshold))
    pyplot.hold('True')

numpy.set_printoptions(precision=2)
pyplot.xlabel('Delay time (ms)')
pyplot.ylabel('Melted fraction')
pyplot.legend(loc="upper left", bbox_to_anchor=(0.8,0.85))
#pyplot.xlim([0,130])
pyplot.ylim([-0.03,1.03])
pyplot.show()

print 'DONE'


