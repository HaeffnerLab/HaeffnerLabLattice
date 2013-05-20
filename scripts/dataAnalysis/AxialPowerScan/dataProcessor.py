import numpy as np
import labrad
from matplotlib import pyplot
from scripts.scriptLibrary import dvParameters
from scipy.interpolate import interp1d 
from scipy import optimize

class dataProcessor():

    def __init__(self, params):       
        self.pulsedTime = float(params['pulsedTime'])
        self.coolingTime = float(params['coolingTime'])
        self.switching = float(params['switching'])
        self.iterations = int(params['iterations'])
        self.cycleTime = float(params['cycleTime'])
    
    def addData(self, timetags):
        self.timetags = timetags
        self.addData = None
    
    def sliceArr(self, arr, start, duration, cyclenumber = 1, cycleduration = 0 ):
        '''Takes a np array arr, and returns a new array that consists of all elements between start and start + duration modulo the start time
        If cyclenumber and cycleduration are provided, the array will consist of additional slices taken between start and 
        start + duration each offset by a cycleduration. The additional elements will added modulo the start time of their respective cycle'''
        starts = [start + i*cycleduration for i in range(cyclenumber)]
        criterion = reduce(np.logical_or, [(start <= arr) & (arr <=  start + duration) for start in starts])
        result = arr[criterion]
        if cycleduration == 0:
            if start != 0:
                result = np.mod(result, start)
        else:
            result = np.mod(result - start, cycleduration)
        return result
    
    def process(self):
        self.processBinning()
        self.processPowerScan()
        return (self.pwrList,self.fluor)
    
    def processBinning(self):
        '''shows binning at the highest power'''
        times = self.timetags[:,1]
        powers = self.timetags[:,0]
        maxpower =  np.max(np.unique(self.timetags[:,0]))
        tags = times[np.where(powers == maxpower)]
        tags = np.mod(tags, self.cycleTime)
        binTime = 25.0*10**-6
        self.bins = np.arange(self.cycleTime / binTime) * binTime
        self.binned = np.histogram(tags, self.bins)[0]
        collectionTime = self.cycleTime * self.iterations
        self.binned = self.binned / (self.iterations * binTime) #Counts per sec
        
    def processPowerScan(self):
        '''plots the total number of differential counts during the pulsed times vs the power at the time of pulsing'''
        times = self.timetags[:,1]
        powers = self.timetags[:,0]
        self.pwrList =  np.unique(self.timetags[:,0])
        fluor = []
        for pwr in self.pwrList:
            tags = times[np.where(powers == pwr)]
            countsBackground = self.sliceArr(tags,  start = self.coolingTime + self.switching, duration =  self.pulsedTime, cyclenumber = self.iterations, cycleduration = self.cycleTime)
            countsSignal = self.sliceArr(tags,  start = self.coolingTime + self.switching + self.pulsedTime, duration =  self.pulsedTime, cyclenumber = self.iterations, cycleduration = self.cycleTime)
            bgsubtracted = countsSignal.size - countsBackground.size
            #converting to Counts/Sec
            collectionTime = self.pulsedTime * self.iterations
            bgsubtracted = bgsubtracted / float(collectionTime)
            fluor.append(bgsubtracted)
        self.fluor = np.array(fluor)
        
    def makePlot(self):
        pyplot.figure()
        ax = pyplot.subplot(121) 
        pyplot.plot(self.bins[0:-1],self.binned)
        pyplot.title('Max Power Average Iteration')
        pyplot.xlabel('Sec')
        pyplot.ylabel('Counts/Sec')
        pyplot.subplot(122, sharey = ax) 
        pyplot.title('Power Scan')
        pyplot.plot(self.pwrList, self.fluor)
        pyplot.xlabel('AO Power dBM')
        pyplot.ylabel('Counts/Sec')
        pyplot.show()
        
    def sliceArr(self, arr, start, duration, cyclenumber = 1, cycleduration = 0 ):
        '''Takes a np array arr, and returns a new array that consists of all elements between start and start + duration modulo the start time
        If cyclenumber and cycleduration are provided, the array will consist of additional slices taken between start and 
        start + duration each offset by a cycleduration. The additional elements will added modulo the start time of their respective cycle'''
        starts = [start + i*cycleduration for i in range(cyclenumber)]
        criterion = reduce(np.logical_or, [(start <= arr) & (arr <=  start + duration) for start in starts])
        result = arr[criterion]
        if cycleduration == 0:
            if start != 0:
                result = np.mod(result, start)
        else:
            result = np.mod(result - start, cycleduration)
        return result
    
class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value

class fitSaturation():
    
    def __init__(self, calibration, data, range = None, detuning = None, name = None):
        self.name = name
        self.calibAOPowers = calibration.transpose()[0]
        self.calibLightPower = calibration.transpose()[1]
        self.dataAOPowers = data.transpose()[0]
        self.dataFluor = data.transpose()[1]
        self.range = range
        self.detuning = detuning
        self.dofit()
        
    def fit(self, function, parameters, y, x = None):
        def f(params):
            i = 0
            for p in parameters:
                p.set(params[i])
                i += 1
            return y - function(x)
        if x is None: x = numpy.arange(y.shape[0])
        p = [param() for param in parameters]
        optimize.leastsq(f, p) #weight proportional to spacing
        return f
        
    def dofit(self):
        #first need to convert AO powers of the data to intensity using the calibration trace
        #interpolate between the calibration and extract the intensity of the data
        f = interp1d(self.calibAOPowers, self.calibLightPower)
        self.powers = f(self.dataAOPowers)
        #define the fitting function
        MaxFluor = Parameter(40000)
        xscale = Parameter(0.001) #lightpower =  xscale * saturation
        if self.range is not None:
            inrange = (self.powers <= self.range[1]) * (self.powers >= self.range[0])
            self.powers = self.powers[inrange]
            self.dataFluor = self.dataFluor[inrange]
        if self.detuning is not None:
            detuning = self.detuning
            def fitfunc(x): return (2.0 * MaxFluor()) * (x/xscale())**2 * 0.25 / (0.25 + detuning**2 + .5 * (x/xscale())**2)
            self.fit(fitfunc, [MaxFluor, xscale], self.dataFluor , self.powers)
            print 'using detuning {} Gamma'.format(detuning)
        else:
            detuning = Parameter(1)
            def fitfunc(x): return (2.0 * MaxFluor()) * (x/xscale())**2 * 0.25 / (0.25 + detuning()**2 + .5 * (x/xscale())**2)
            self.fit(fitfunc, [MaxFluor, xscale, detuning], self.dataFluor , self.powers)
            print 'detuning', detuning()
            self.detuning = detuning()
        self.fitfunc = fitfunc
        print 'max fluorescence', MaxFluor()
        print 'xscale', np.abs(xscale())
        self.xscalefit = np.abs(xscale())
       
    
    def makePlot(self):
        minx = np.min(self.powers)
        maxx = np.max(self.powers)
        xvals = np.linspace(minx, maxx, self.powers.size*100)
        yvals = self.fitfunc(xvals)
        pyplot.figure()
        pyplot.plot(self.powers, self.dataFluor, 'o', markersize=4)
        pyplot.plot(xvals,yvals)
        pyplot.ylim(ymin = 0)
        s = "Pulsed Axial Power Scan {}\n".format(self.name)
        s = s + "Detuning {0:.2f} Gamma\n".format(self.detuning)
        maxsat = maxx / self.xscalefit
        s = s +  "Max Saturation {0:.0f}\n".format(maxsat)
        s = s + "Power for s = 1 : {0:.2f} microwatt\n".format(1000 * self.xscalefit)
        Isat = 4.33*10**-7 #mW / micron^2, #see e.g aarhus phd peter staanum
        waist = np.sqrt(self.xscalefit/ Isat) / 2.0
        s = s + "Waist of ~{0:.0f} micron".format(waist)
        pyplot.text(0.5, 10000.0 , s )#,  verticalalignment='top')
        pyplot.xlabel('397 Power mW')
        pyplot.ylabel('Fluorescence Counts/Sec')
        ax = pyplot.twiny()
        pyplot.xlabel("Saturation =  Omega / Gamma")
        pyplot.xlim(xmin = minx / self.xscalefit, xmax = maxx/ self.xscalefit)
        pyplot.show()
    
if __name__ == '__main__':
    cxn = labrad.connect()
    dv = cxn.data_vault
    experiment = 'pulsedScanAxialPower'
    
    def process(dataset):
        dv.cd(['', 'Experiments', experiment, dataset])
        dv.open(1)
        data = dv.get().asarray
        params = dict(dv.get_parameters())
        dp = dataProcessor(params)
        dp.addData(data)
        pwr,fluor = dp.process()
        name = dv.new('scan',[('Power', 'dBm')],[('Counts','Counts/sec','Counts/sec')] )
        dvParameters.saveParameters(dv, params)
        dv.add_parameter('plotLive',True)
        dv.add(np.vstack((pwr,fluor)).transpose())
        dp.makePlot()
    
    def fit((dataset,number), calibName, detuning = None, range = None): 
        dv.cd(['', 'Experiments', experiment, dataset])
        trace = dv.open(number)
        data = dv.get().asarray
        dv.cd(['', 'QuickMeasurements'])
        dv.open(int(calibName))
        calibration = dv.get().asarray
        ft = fitSaturation(calibration, data, detuning = detuning, range = range, name = dataset)
        ft.makePlot()
        
    #process('2012May16_1829_53')
    fit(('2012May18_1535_43',2), '143', detuning =12.5)
    #fit(('2012May18_1541_04',2), '143', detuning = -0.5, range = (0, 0.3))