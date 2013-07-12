import labrad
from matplotlib import pyplot

info = [('2013Jun28', '1924_31', 'b'),
#         ('2013Jun28', '1925_51'),
        ('2013Jun28', '1926_42', 'g'),
        ('2013Jun28', '1927_29', 'r'),
        ('2013Jun28', '1928_29', 'c'),
        
        ]

cxn = labrad.connect()
dv = cxn.data_vault

for date, datasetName, color in info:
    dv.cd( ['','Experiments','Blue Heat RabiFlopping',date,datasetName])
    dv.open(1)
    data = dv.get().asarray
    times, probs = data.transpose()
    heating_us = dv.get_parameter('Heating.blue_heating_duration')['us']
    pyplot.plot(times, probs, 'o-', label = r'Heating, {0} $\mu s$'.format(heating_us), color = color)

pyplot.title('Pulsed Heating', fontsize = 32)
pyplot.xlabel(u'Excitation time $\mu s$', fontsize = 32)
pyplot.ylabel('Excitation probability', fontsize = 32)
pyplot.ylim([0,1.0])
pyplot.legend(prop={'size':26})
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.show()