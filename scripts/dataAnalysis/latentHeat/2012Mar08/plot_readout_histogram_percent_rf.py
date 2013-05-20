import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

meltingThreshold = 2800
totalTraces = 30
datasets = ['2012Mar08_2022_35', '2012Mar08_2023_27', '2012Mar08_2024_52']

#['2012Mar08_1947_54', '2012Mar08_1948_56', '2012Mar08_1947_02', '2012Mar08_1942_39',
#            '2012Mar08_1944_11', '2012Mar08_1945_04', '2012Mar08_1946_03'] # rf powers

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Melting percentage with varying compensations')

comp_tilt = [13.48, 30.5, 40.5]
percent_melt = []

for datasetName in datasets:
    #getting parameters
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
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

pyplot.plot(comp_tilt, percent_melt, '-o')
pyplot.xlabel('Compensation Tilt')
pyplot.ylabel('Melted fraction')
pyplot.ylim([0,1.0])
pyplot.show()