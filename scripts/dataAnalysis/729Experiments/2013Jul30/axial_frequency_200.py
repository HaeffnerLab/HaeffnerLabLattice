import labrad
from matplotlib import pyplot

info = [
        ('2013Jul30', '1354_25', '0ms delay'),
        ('2013Jul30', '1401_54', '200ms delay'),
        ]

cxn = labrad.connect()
dv = cxn.data_vault

for date, datasetName, comment in info:
    dv.cd( ['','Experiments','RabiFlopping',date,datasetName])
    dv.open(1)
    data = dv.get().asarray
    transpose = data.transpose()
    times = transpose[0]
    flops = transpose[1:]
    for ion, flop in enumerate(flops):
        pyplot.plot(times, flop, 'o-', label = comment)

pyplot.title('f_z = 200 KHz', fontsize = 32)
pyplot.suptitle('2013Jul30, 1354_25, 1401_54')
pyplot.xlabel(u'Excitation Duration ($\mu s$)', fontsize = 32)
pyplot.ylabel('Excitation probability', fontsize = 32)
pyplot.ylim([0,1.0])
pyplot.legend(prop={'size':26})
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.grid(True, 'major')
pyplot.show()