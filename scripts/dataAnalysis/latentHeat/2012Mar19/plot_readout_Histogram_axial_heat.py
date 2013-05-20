import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

totalTraces = 100
datasets = ['2012Mar20_0127_37', '2012Mar20_0117_49', '2012Mar20_0129_49',
            '2012Mar20_0132_28', '2012Mar20_0114_32']


refSigs = []
detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Melting percentage using readout beam: all heating')

for datasetName in datasets:
    print 'Getting heating counts...'
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    xtal_record = dv.get_parameter('xtal_record')
#    
    # readout range
    heatStart = (initial_cooling + heat_delay ) # / 10.0**6 #in seconds
    heatEnd = (initial_cooling + heat_delay +axial_heat ) 
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay ) 
    stopReadout = startReadout + readout_time 
    print datasetName, heatStart, heatEnd, startReadout, stopReadout
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
     # get blue heating signal to normalize to    
    for dataset in range(1,totalTraces+1):
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        refReadout = numpy.count_nonzero((heatStart <= timetags) * (timetags <= heatEnd))
        refSigs.append(refReadout) 
    print 'Now Readout...'     
    print 'Readout time :', stopReadout - startReadout
    print 'Heating time :', heatEnd - heatStart
    for dataset in range(1,totalTraces+1):
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        refReadout = numpy.count_nonzero((heatStart <= timetags) * (timetags <= heatEnd))
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        normCounts = (float(refReadout) / float(max(refSigs))) * (countsReadout)  
        detectedCounts.append(countsReadout)
    print countsReadout, refReadout
print numpy.shape(detectedCounts)
print 'Done'
pyplot.hist(detectedCounts, 60)
pyplot.show()