import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import numpy as np


class SequencePlotter():
    """Can be used to plot the human readable form of a pulse sequence"""
    def __init__(self, sequence, channels):
        self.seq = sequence
        self.channels = channels
        self.plot = pyplot.figure()
    
    def makeNameDict(self):
        #swapping names of channels first
        chan = self.channels
        names = np.copy(chan[:,0])
        chan[:,0] = chan[:,1]
        chan[:,1] = names
        d = dict(chan)
        return d
    
    def extractInfo(self):        
        times = np.array(self.seq.transpose()[0], dtype = np.float)
        l =  self.seq.transpose()[1]
        flatten = lambda x: [int(i) for i in x]
        switches = np.array( map(flatten, l) )
        switches = switches.transpose()
        return times,switches
    
    def getCoords(self, times, switches):
        '''takes the switching times and converts it a list of coordiantes for plotting'''
        x = [times[0]]
        y = [switches[0]]   
        prev = switches[0]
        for i,switch in enumerate(switches[:-1]):
            if switch > prev:
                x.extend([times[i]]*2)
                y.extend([0,1])
            elif switch < prev:
                x.extend([times[i]]*2)
                y.extend([1,0])
            prev = switch
        x.append(times[-2])
        y.append(switches[-2])
        return np.array(x),np.array(y)
                 
    def makePlot(self):
        times,switches = self.extractInfo()
        nameDict = self.makeNameDict()
        offset = 0
        for number,channel in enumerate(switches):
            if channel.any(): #ignore empty channels
                x,y = self.getCoords(times, channel)
                y = 3 * y + offset #offset the y coordinates
                offset = offset + 4
                label = nameDict[str(number)]
                pyplot.plot(x, y, label = label)
        pyplot.legend()
        pyplot.xlabel('Time (sec)')
        pyplot.show()


if __name__ == '__main__':
    import labrad
    from latentHeat import LatentHeatGlobalHeat as sequence
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = sequence(pulser)
    pulser.new_sequence()
    params = {
              'initial_cooling': 1000e-3,
              'heat_delay':1000e-3,
              'axial_heat':1000e-3,
              'readout_delay':1000e-3,
              'readout_time':1000e-3,
              'xtal_record':1000e-3,
              'cooling_ampl_866':-11.0,
              'heating_ampl_866':-11.0,
              'readout_ampl_866':-11.0,
              'xtal_ampl_866':-11.0,
              'cooling_freq_397':103.0,
              'cooling_ampl_397':-13.0,
              'readout_freq_397':115.0,
              'readout_ampl_397':-13.0,
              'xtal_freq_397':103.0,
              'xtal_ampl_397':-11.0,
              'heating_freq_397':130.0,
              'heating_ampl_397':-11.0,
              }
    seq.setVariables(**params)
    seq.defineSequence()
    #pulser.program_sequence() 
    hr = pulser.human_readable().asarray
    channels = pulser.get_channels().asarray
    sp = SequencePlotter(hr, channels)
    sp.makePlot()