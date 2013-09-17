import labrad
from matplotlib import pyplot

info = [('2013Sep04', '2212_50', 'black'), #0
#         ('2013Sep04', '2215_47', 'b'), #50
#         ('2013Sep04', '2217_35', 'g'), #100
#         ('2013Sep04', '2218_52', 'r'), #200
#         ('2013Sep04', '2247_28', 'magenta'), #1000
#         ('2013Sep04', '2219_50', 'blue'), #2000
        ('2013Sep04', '2222_19', 'green'), #10000
        ('2013Sep04', '2255_17', 'red'), #15000
        ('2013Sep04', '2249_41', 'orange'), #20000
        ('2013Sep04', '2305_48', 'magenta'), #30000
        ]
ion_selection = 0


cxn = labrad.connect()
dv = cxn.data_vault

for date, datasetName, color in info:
    dv.cd( ['','Experiments','Blue Heat RabiFlopping',date,datasetName])
    dv.open(1)
    data = dv.get().asarray
    times, probs = data.transpose()[[0, 1 + ion_selection],:]
    heating_us = dv.get_parameter('Heating.blue_heating_delay_after')['us']
    pyplot.plot(times, probs, 'o-', label = r'Delay, {0} $\mu s$'.format(heating_us), color = color)

pyplot.title('Ion {}'.format(ion_selection), fontsize = 32)
pyplot.xlabel(u'Excitation Heating time $\mu s$', fontsize = 16)
# pyplot.ylabel('Excitation probability', fontsize = 32)
pyplot.ylim([0,1.0])
pyplot.legend(prop={'size':14})
pyplot.tick_params(axis='both', which='major', labelsize=16)
pyplot.tight_layout()
pyplot.savefig('Heating long delay, Ion {}.png'.format(ion_selection))
pyplot.show()