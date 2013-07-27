import labrad
from matplotlib import pyplot

info = [('2013Jul25', '1527_00', 'b',r'0 $\mu s$'),
        ('2013Jul25', '1531_13', 'g',r'10 $\mu s$'),
        ('2013Jul25', '1529_55', 'r',r'20 $\mu s$'),
        ('2013Jul25', '1525_42', 'k',r'50 $\mu s$'),
        ('2013Jul25', '1532_15', 'm',r'75 $\mu s$'),
        ('2013Jul25', '1533_19', 'c',r'125 $\mu s$'),
        
        ]

cxn = labrad.connect()
dv = cxn.data_vault

for date, datasetName, color, label in info:
    dv.cd( ['','Experiments','Blue Heat RabiFlopping',date,datasetName])
    dv.open(1)
    data = dv.get().asarray
    times, probs = data.transpose()
    pyplot.plot(times, probs, 'o-', label = label, color = color)

pyplot.title('One ion Pulsed heating, sideband readout', fontsize = 32)
pyplot.xlabel(u'Excitation time $\mu s$', fontsize = 32)
pyplot.ylabel('Excitation probability', fontsize = 32)
pyplot.ylim([0,1.0])
pyplot.legend(prop={'size':26})
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.show()