import labrad
from matplotlib import pyplot

info = [('2013Sep04', '2150_20', 'k'),
        ('2013Sep04', '2211_19', 'b'),
        ('2013Sep04', '2212_50', 'g'),
        ('2013Sep04', '2209_47', 'r'),
        ('2013Sep04', '2206_19', 'orange'),
        ]
ion_selection = 3


cxn = labrad.connect()
dv = cxn.data_vault

for date, datasetName, color in info:
    dv.cd( ['','Experiments','Blue Heat RabiFlopping',date,datasetName])
    dv.open(1)
    data = dv.get().asarray
    times, probs = data.transpose()[[0, 1 + ion_selection],:]
    heating_us = dv.get_parameter('Heating.blue_heating_duration')['us']
    pyplot.plot(times, probs, 'o-', label = r'Heating, {0} $\mu s$'.format(heating_us), color = color)

pyplot.title('Ion {}'.format(ion_selection), fontsize = 32)
pyplot.xlabel(u'Excitation time $\mu s$', fontsize = 16)
# pyplot.ylabel('Excitation probability', fontsize = 32)
pyplot.ylim([0,1.0])
pyplot.legend(prop={'size':14})
pyplot.tick_params(axis='both', which='major', labelsize=16)
pyplot.tight_layout()
pyplot.savefig('Heating time, Ion {}.png'.format(ion_selection))
pyplot.show()