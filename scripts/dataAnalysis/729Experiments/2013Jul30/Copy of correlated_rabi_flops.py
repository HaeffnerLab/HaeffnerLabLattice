import labrad
from matplotlib import pyplot

info = [('2013Aug26', '2125_21')]

cxn = labrad.connect()
dv = cxn.data_vault

for date, datasetName in info:
    dv.cd( ['','Experiments','RabiFlopping',date,datasetName])
    dv.open(1)
    data = dv.get().asarray
    transpose = data.transpose()
    times = transpose[0]
    flops = transpose[1:]
    for ion, flop in enumerate(flops):
        pyplot.plot(flop, 'o-', label = r'Ion, {0}'.format(ion))

pyplot.title('Correlated Fluctuations Across Ion Chain', fontsize = 32)
pyplot.suptitle('2013Jul30, 1637_53')
pyplot.xlabel(u'Repetition', fontsize = 32)
pyplot.ylabel('Excitation probability', fontsize = 32)
pyplot.ylim([0,1.0])
pyplot.legend(prop={'size':26})
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.grid(True, 'major')
pyplot.show()