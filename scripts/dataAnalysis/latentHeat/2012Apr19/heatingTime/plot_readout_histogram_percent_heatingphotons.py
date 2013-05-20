import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

#info in the format, [(label, melting threshold, totalTraces, list of datasets),...]
info =[
       ('10ions RF -3.5dBm', 225, 50, ['2012Apr19_1636_17','2012Apr19_1639_12','2012Apr19_1637_26','2012Apr19_1640_40','2012Apr19_1643_10','2012Apr19_1645_06']),
       ('10ions RF -4.2dBm', 187, 50, ['2012Apr19_1709_12','2012Apr19_1710_14','2012Apr19_1712_08','2012Apr19_1713_19','2012Apr19_1717_32']),
       ('10ions RF -5.0dBm', 200, 50, ['2012Apr19_1749_14','2012Apr19_1750_24','2012Apr19_1751_39','2012Apr19_1753_24','2012Apr19_1754_39','2012Apr19_1756_20']),
       ('10ions RF -7.0dBm (close to zigzag)', 180, 50, ['2012Apr19_1812_35','2012Apr19_1811_24','2012Apr19_1813_37','2012Apr19_1814_42','2012Apr19_1815_43']),
       ('15ions RF -3.5dBm', 250, 50, ['2012Apr19_1935_17', '2012Apr19_1937_28','2012Apr19_1939_32', '2012Apr19_1940_47','2012Apr19_1942_22']),
       ('15ions RF -7.0dBm, zigzag', 250, 50, ['2012Apr19_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [203455,203604,203812,203942,204211]]),
       ] 

#make figure
figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Melting percentage during heating, no delay')


def energyAdded(photonsScattered):
    ###need to verify these numbers and subtract the background
    detuning = 280*10.0**6#Hz
    objectiveEfficiency= 0.025 #Kirchmair thesis, 2.5% of solid angle
    pelicalSplit = .70
    PMTEfficiency = .50
    recordEffieincy = .50 #FPGA
    detectionEfficiency = PMTEfficiency * pelicalSplit * objectiveEfficiency * recordEffieincy
    energy = detuning * photonsScattered / detectionEfficiency
    return energy

def errorBarSimple(trials, prob):
    #look at wiki http://en.wikipedia.org/wiki/Checking_whether_a_coin_is_fair
    '''returns 1 sigma error bar'''
    Z = 1.0
    s = numpy.sqrt(prob * (1.0 - prob) / float(trials))
    err = Z * s
    return (err,err)

def arangeByFirst(one,rest):
    '''given n arrays, returns them sorted in the order of the increasing first array'''
    tosort = one.argsort()
    sortedArrs = []
    one = one[tosort]
    for arr in rest:
        sortedArrs.append(arr[tosort])
    return one,sortedArrs
    
for i in range(len(info)):
    label = info[i][0]
    meltingThreshold = info[i][1]
    totalTraces = info[i][2]
    datasets = info[i][3]
    energyHeat = []
    percent_melt = []
    error_bars = []
    for datasetName in datasets:
        print datasetName
        #getting parameters
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
        dv.open(1)    
        initial_cooling = dv.get_parameter('initial_cooling')
        heat_delay = dv.get_parameter('heat_delay')
        axial_heat = dv.get_parameter('axial_heat')
        readout_delay = dv.get_parameter('readout_delay')
        readout_time = dv.get_parameter('readout_time')
        #heatRange
        startHeat = initial_cooling + heat_delay
        endHeat = startHeat + axial_heat
        #readout range
        startReadout =  endHeat + readout_delay
        stopReadout = startReadout + readout_time 
        #data processing on the fly
        dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
        melted = 0
        heatingPhotons = 0
        for dataset in range(1,totalTraces+1):
            dv.open(int(dataset))
            timetags = dv.get().asarray[:,0]
            countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
            heatingPhotons += numpy.count_nonzero((startHeat <= timetags) * (timetags <= endHeat))
            if countsReadout < meltingThreshold: # melting is less counts
                melted +=1
        energy = energyAdded(heatingPhotons / float(totalTraces))
        energyHeat.append(energy)       
        perc = melted / float(totalTraces)
        percent_melt.append(perc)
        error_bars.append(errorBarSimple(totalTraces, perc))
    energyHeatTHZ = numpy.array(energyHeat) / 10.0**12
    percent_melt = numpy.array(percent_melt)
    error_bars = numpy.array(error_bars)
    energyHeatTHZ, [percent_melt,error_bars] = arangeByFirst(energyHeatTHZ, [percent_melt,error_bars])
    pyplot.errorbar(energyHeatTHZ, percent_melt, fmt = '-o', label = label, yerr = error_bars.transpose())
    pyplot.hold('True')

pyplot.xlabel('Energy added (THz)')
pyplot.ylabel('Melted fraction')
pyplot.legend()
#redo x domain
xmin, xmax = pyplot.xlim() 
pyplot.xlim(0, 1.5*xmax)
#show
pyplot.show()
cxn.disconnect()