from matplotlib import pyplot


pulsed_heating_duration_cooled = [0, 10, 7, 10, 50, 20]
alpha_cooled = [0, 1.86, 1.1, 1.98, 15.2, 7.5]

pulsed_heating_duration = [0, 50, 20, 10, 15, 25, 30, 35, 40, 45, 60, 80, 100]
alpha = [0, 17.4, 7.8, 2.1, 4.4, 10.2, 12.1, 14, 15.8, 16.6, 16.1, 10.0, 5.3]

pyplot.plot(pulsed_heating_duration_cooled, alpha_cooled, 'or', label = 'sideband cooling', markersize = 8)
pyplot.plot(pulsed_heating_duration, alpha, 'ob', label = 'doppler cooling', markersize = 8)
pyplot.tight_layout()
pyplot.title('Pulsed Heating Displacement', fontsize = 32)
pyplot.xlabel('Pulsed Heating Time ($\\mu s$)', fontsize = 26)
pyplot.ylabel(u'Displacement $|\\alpha|$', fontsize = 26)
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.legend(prop={'size':22})
pyplot.show()