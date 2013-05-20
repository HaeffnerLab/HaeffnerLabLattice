import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

meltingThreshold = 100 
totalTraces = 50
datasets =   [['2012Apr16_1807_50','2012Apr16_1808_44','2012Apr16_1809_49','2012Apr16_1811_04','2012Apr16_1812_25',
               '2012Apr16_1813_55','2012Apr16_1816_59','2012Apr16_1818_25','2012Apr16_1820_08'],
              ['2012Apr16_2044_39','2012Apr16_2043_36','2012Apr16_2042_03','2012Apr16_2039_50',
               '2012Apr16_2038_11','2012Apr16_2045_33','2012Apr16_2046_59','2012Apr16_2048_35','2012Apr16_2050_43'],
               ['2012Apr16_2003_38','2012Apr16_2005_00','2012Apr16_2007_13','2012Apr16_2008_39','2012Apr16_2010_11']]
#  RF with varying delay [['2012Apr16_1947_53','2012Apr16_1958_37','2012Apr16_2000_11','2012Apr16_1948_59',
#             '2012Apr16_1950_32','2012Apr16_1952_27'],
#             ['2012Apr16_2054_21','2012Apr16_2055_21','2012Apr16_2056_29','2012Apr16_2100_06',
#              '2012Apr16_2057_52','2012Apr16_2101_54','2012Apr16_2104_07','2012Apr16_2106_51'],
#             ['2012Apr16_2011_56','2012Apr16_2012_56','2012Apr16_2014_07','2012Apr16_2015_29',
#              '2012Apr16_2017_14','2012Apr16_2020_22','2012Apr16_2022_54']] 
            #['2012Apr16_2150_52','2012Apr16_2151_56','2012Apr16_2153_06','2012Apr16_2154_08','2012Apr16_2155_31']

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
title = 'Varying heating times at different Rf'
pyplot.suptitle(title)

refSigs = []

for x in range(len(datasets)):
    heat_times = []
    delay_times = []
    percent_melt = []
    for datasetName in datasets[x]:
        refs = 0
        #getting parameters
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
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
    pyplot.plot(heat_times, percent_melt, '-o', label = 'RF = {0} dBm'.format(rf_power))
    pyplot.hold('True')

numpy.set_printoptions(precision=2)
pyplot.xlabel('Heating time (ms)')
pyplot.ylabel('Melted fraction')
pyplot.legend(loc="upper left", bbox_to_anchor=(0.8,0.9))
#pyplot.xlim([0,130])
pyplot.ylim([-0.05,1.05])
pyplot.show()

print 'DONE'

