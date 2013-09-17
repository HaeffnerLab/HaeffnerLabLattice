from matplotlib import pyplot


pulsed_heating_duration = [0, 20, 40, 80, 100]
alpha_ion_4 = [0, 2.31, 5.65,  7.85, 10.6]
alpha_ion_3 = [0, 1.68, 2.77, 1.84, 6.1]
alpha_ion_2 = [0, 0.98, 2.14, 2.91, 1.44]
alpha_ion_1 = [0, 0.72, 0.86, 3.65, 1.585253]

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