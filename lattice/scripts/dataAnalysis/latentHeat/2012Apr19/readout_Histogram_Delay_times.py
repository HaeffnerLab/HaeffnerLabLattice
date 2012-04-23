import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
from scipy.stats import norm
import matplotlib.mlab as mlab
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

totalTraces = 50
meltingThreshold = 180 
datasets = ['2012Apr19_1647_06','2012Apr19_1648_25','2012Apr19_1649_33','2012Apr19_1651_16',
               '2012Apr19_1653_11', '2012Apr19_1655_13','2012Apr19_1657_09','2012Apr19_1659_25','2012Apr19_1702_19']

mus = []
sigs = []
detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Mean and sigmas of melted histograms')

delay_times = []
for datasetName in datasets:
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    delay_times.append(readout_delay * 10.**3)
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    xtal_record = dv.get_parameter('xtal_record')
    
    # readout range
    heatStart = (initial_cooling + heat_delay ) # / 10.0**6 #in seconds
    heatEnd = (initial_cooling + heat_delay +axial_heat ) 
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay ) 
    stopReadout = startReadout + readout_time 
    print datasetName, heatStart, heatEnd, startReadout, stopReadout
    print 'Heating time :', heatEnd - heatStart
    print 'Delay time :', readout_delay
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
        
    for dataset in range(1,totalTraces+1):
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        #normCounts = (float(refReadout) / float(max(refSigs))) * (countsReadout)  
        detectedCounts.append(countsReadout)

    dC = numpy.array(detectedCounts)
    meltHist = dC[(dC < meltingThreshold).nonzero()]
    (mu, sigma) = norm.fit(meltHist)
    print mu, sigma
    mus.append(mu)
    sigs.append(sigma)
    #n, bins, patches = pyplot.hist(meltHist, 20)
    #y = mlab.normpdf( bins, mu, sigma)
#pyplot.hist(detectedCounts, 60)
#l = pyplot.plot(bins, y*(9/max(y)), 'r--', linewidth=2)
pyplot.plot(delay_times, mus, '-o', label = 'means')
pyplot.plot(delay_times, sigs, '-o', label = 'sigmas') 
pyplot.legend()
pyplot.show()
print 'Done'