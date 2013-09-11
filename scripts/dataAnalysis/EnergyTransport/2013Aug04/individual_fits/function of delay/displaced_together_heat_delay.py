from matplotlib import pyplot


pulsed_heating_duration = [0, 20, 40, 80, 100]
alpha_ion_4 = [0, 0.859350, 3.14,  4.45, 6.4]
alpha_ion_3 = [0, 1.89, 3.077, 2.04, 7.23]
alpha_ion_2 = [0, 1.5474, 2.79, 4.88, 2.05]
alpha_ion_1 = [0, 0.93, 1.0, 4.6, 1.585253]

pyplot.plot(pulsed_heating_duration, alpha_ion_4, 'og--', label = 'ion 4', markersize = 8)
pyplot.plot(pulsed_heating_duration, alpha_ion_3, 'or--', label = 'ion 3', markersize = 8)
pyplot.plot(pulsed_heating_duration, alpha_ion_2, 'ok--', label = 'ion 2', markersize = 8)
pyplot.plot(pulsed_heating_duration, alpha_ion_1, 'ob--', label = 'ion 1', markersize = 8)
pyplot.tight_layout()
pyplot.title('Pulsed Heating Displacement', fontsize = 32)
pyplot.xlabel('Pulsed Heating Time ($\\mu s$)', fontsize = 26)
pyplot.ylabel(u'Displacement $|\\alpha|$', fontsize = 26)
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.legend(prop={'size':22})
pyplot.show()