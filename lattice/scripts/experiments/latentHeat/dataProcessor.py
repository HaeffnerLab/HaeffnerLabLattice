import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

datasets = ['2012Apr16_2133_32']
directory = ['','Experiments','LatentHeat_no729_autocrystal']

class data_process():
    def __init__(self, cxn , datasets, directory):
        self.dv = cxn.data_vault
        self.datasets = datasets
        self.directory = directory
        
    def binning(self):
        refSigs = [] #list of readouts
        for dataset in self.datasets:
            self.navigateDirectory(dataset)
        traces = len(self.dv.dir()[1])
        if not traces: raise Exception("No saved timetags")
        for trace in range(1, traces+1):
            dv.open(int(dataset))
            timetags = dv.get().asarray[:,0]
            refReadout = numpy.count_nonzero((heatStart <= timetags) * (timetags <= heatEnd))
            refSigs.append(refReadout)  
        
    def navigateDirectory(self, dataset):
        self.dv.cd(directory)
        self.dv.cd(dataset)
        self.dv.cd('timetags')



if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    dp = data_process(cxn, datasets, directory)
    dp.binning()
    print 'done'