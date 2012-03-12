import numpy as np
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

meltingThreshold = 2500
totalTraces = 30
minFreq = 14.999*10**6 #Hz
maxFreq = 15.001*10**6 #Hz

def getFFTpwr(timetags):
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0
    pwr = pwr / timetags.size
    del(mat,fft)
    return pwr

excludeStat = 0.05 #discard traces with fewer than this percentage of events i.e if melts once, don't plot
experiment = 'LatentHeat_no729_autocrystal'
datasets = ['2012Mar08_1920_06', '2012Mar08_1921_47', '2012Mar08_1926_43']

#['2012Mar08_1918_28', '2012Mar08_1920_06','2012Mar08_1922_59','2012Mar08_1919_12','2012Mar08_1921_47','2012Mar08_1920_53','2012Mar08_1924_11','2012Mar08_1926_43']
#['2012Mar08_1920_06', '2012Mar08_1921_47', '2012Mar08_1926_43']

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Separated Traces')


for datasetName in datasets:
    melted = 0
    crystal = 0
    #getting parameters
    dv.cd(['','Experiments',experiment,datasetName])
    dv.open(1)
    recordTime = dv.get_parameter('recordTime')
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    freqRes = 1.0 / (float(readout_time) / 10.0**6)
    freqs = np.arange(minFreq,maxFreq,freqRes)
    meltedFFT = np.zeros_like(freqs)
    notmeltedFFT = np.zeros_like(freqs)
    #readout range
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay ) / 10.0**6 #now in seconds
    stopReadout = startReadout + readout_time / 10.0**6 #now in seconds
    #data processing on the fly
    dv.cd(['','Experiments',experiment,datasetName,'timetags'])
    melted = 0
    for dataset in range(1,totalTraces+1):
        print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = np.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        newfft = getFFTpwr(timetags)
        if countsReadout < meltingThreshold:
            meltedFFT += newfft
            melted += 1
        else:
            notmeltedFFT += newfft
            crystal += 1
    #normalizing and excluding ones that don't have enough statistics
    if melted > excludeStat * totalTraces:
        meltedFFT = meltedFFT / float(melted)
        pyplot.plot(freqs, meltedFFT, label = 'Melted {0}, heating {1} ms'.format(datasetName,axial_heat/10.**3))
    if crystal > excludeStat * totalTraces:
        notmeltedFFT = notmeltedFFT / float(crystal)
        pyplot.plot(freqs, notmeltedFFT, label = 'Crystallized {0}, heating {1} ms'.format(datasetName,axial_heat/10.**3))
        
pyplot.legend()
pyplot.show()