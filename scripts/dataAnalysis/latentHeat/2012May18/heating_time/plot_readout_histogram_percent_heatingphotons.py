import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

kb = 2.08366*10**10 #botlzmann contant in units of Hz / Kelvin
#info in the format, [(label, melting threshold, totalTraces, list of datasets),...], ion number

info =[
       ('5 ions RF -3.5dBm', 30000, 200, ['2012May18_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [174535,174755,175012,175234]], 5)
       ] 

#make figure
figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Melting percentage during heating, no delay')

def energyAdded(photonsScattered):
    detuning = 250*10.0**6#Hz
    collectionEfficiency = 1.0*10**-3
    inelasticFraction = 0.95
    energy = detuning * photonsScattered * inelasticFraction / collectionEfficiency
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
    ionnumber = info[i][4]
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
        startHeat = axial_heat + initial_cooling + heat_delay
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
            countsReadout = countsReadout / float(readout_time) #now on counts / sec
            heatingPhotonsSignal = numpy.count_nonzero((startHeat <= timetags) * (timetags <= endHeat))
            heatingPhotonsBackground = numpy.count_nonzero((0 <= timetags) * (timetags <= axial_heat))
            heatingPhotons += heatingPhotonsSignal - heatingPhotonsBackground
            if countsReadout < meltingThreshold: # melting is less counts
                melted +=1
        print 'heating photons', heatingPhotons / float(totalTraces)
        energy = energyAdded(heatingPhotons / float(totalTraces))
        energyHeat.append(energy)       
        perc = melted / float(totalTraces)
        percent_melt.append(perc)
        error_bars.append(errorBarSimple(totalTraces, perc))
    energyHeat = numpy.array(energyHeat)
    energyHeatTHZ = energyHeat / 10.0**12 
    percent_melt = numpy.array(percent_melt)
    error_bars = numpy.array(error_bars)
    energyHeatTHZ, [percent_melt,error_bars] = arangeByFirst(energyHeatTHZ, [percent_melt,error_bars])
    temperaturePerIon = energyHeat / (kb * ionnumber)
    pyplot.errorbar(energyHeatTHZ, percent_melt, fmt = '-o', label = label, yerr = error_bars.transpose())
    pyplot.hold('True')

pyplot.xlabel('Energy Added (THz)')
pyplot.ylabel('Melted fraction')
pyplot.legend()
#redo x domain
xmin, xmax = pyplot.xlim() 
pyplot.xlim(0, 1.5*xmax)
#show
pyplot.show()
cxn.disconnect()