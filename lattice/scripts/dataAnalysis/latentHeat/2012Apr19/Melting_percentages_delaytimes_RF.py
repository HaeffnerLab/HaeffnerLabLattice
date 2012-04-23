import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

meltingThreshold = 180 
totalTraces = 50
datasets =   [['2012Apr19_1647_06','2012Apr19_1648_25','2012Apr19_1649_33','2012Apr19_1651_16',
               '2012Apr19_1653_11', '2012Apr19_1655_13','2012Apr19_1657_09','2012Apr19_1659_25','2012Apr19_1702_19']]#,
               #['2012Apr19_1719_25','2012Apr19_1720_35','2012Apr19_1722_24','2012Apr19_1723_53',
               # '2012Apr19_1725_52','2012Apr19_1728_00','2012Apr19_1730_08'],
               # ['2012Apr19_1758_21','2012Apr19_1759_27','2012Apr19_1800_45','2012Apr19_1804_23',
               #  '2012Apr19_1801_55','2012Apr19_1806_23'],
               #  ['2012Apr19_1816_52','2012Apr19_1822_59','2012Apr19_1824_03','2012Apr19_1817_56','2012Apr19_1818_55',
               #   '2012Apr19_1819_59','2012Apr19_1821_11']]
            
detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
title = 'Varying delay with different Rf'
pyplot.suptitle(title)

heat_times = []
delay_times = []
percent_melt = []
refSigs = []

for x in range(len(datasets)):
    if (x == 0) or (x == 3):
        meltingThreshold = 180 
    else:
        meltingThreshold = 150
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
    pyplot.plot(delay_times, percent_melt, '-o', label = 'RF = {0} dBm'.format(rf_power))
    pyplot.hold('True')

numpy.set_printoptions(precision=2)
pyplot.xlabel('Delay time (ms)')
pyplot.ylabel('Melted fraction')
pyplot.legend(loc="upper left", bbox_to_anchor=(0.8,0.85))
#pyplot.xlim([0,130])
pyplot.ylim([-0.01,1.01])
pyplot.show()

print 'DONE'

