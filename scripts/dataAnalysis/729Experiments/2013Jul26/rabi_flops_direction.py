import labrad
from matplotlib import pyplot

info = [('2013Jul25', '1244_36', 'b','Top beam'),
        ('2013Jul25', '1249_03', 'b',''),
        ('2013Jul25', '1357_11', 'k','Side beam'),
        ('2013Jul25', '1405_36', 'r','Side beam after sideband cooling axial mode'),
        
        ]

cxn = labrad.connect()
dv = cxn.data_vault

for date, datasetName, color, label in info:
    dv.cd( ['','Experiments','RabiFlopping',date,datasetName])
    dv.open(1)
    data = dv.get().asarray
    times, probs = data.transpose()
#     heating_us = dv.get_parameter('Heating.blue_heating_duration')['us']
    pyplot.plot(times, probs, 'o-', label = label, color = color)

pyplot.title('Carrier flops, Axial Frequency increased to 500 KHz', fontsize = 32)
pyplot.xlabel(u'Excitation time $\mu s$', fontsize = 32)
pyplot.ylabel('Excitation probability', fontsize = 32)
pyplot.ylim([0,1.0])
pyplot.legend(prop={'size':26})
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.show()