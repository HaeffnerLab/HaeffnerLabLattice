from matplotlib import pyplot


delay_duration =    [0,     50,     100,     200,     1000,     2000,   10000,  15000,  20000,  30000]
alpha_ion_4 =       [5.65,  4.81,   5.40,    4.71,    7.0,      4.74,   2.57,   4.80,   6.27,   4.61]
alpha_ion_3 =       [2.6,   1.77,   1.71,    2.83,    1.66,      0.69,   3.0,   2.84,   2.34,   2.70]
alpha_ion_2 =       [2.15,   1.66,  0.69,    1.71,    0.49,     1.3,     0.97,   1.85,   1.90,   1.54]

pyplot.plot(delay_duration, alpha_ion_4, 'og--', label = 'ion 4', markersize = 8)
pyplot.plot(delay_duration, alpha_ion_3, 'or--', label = 'ion 3', markersize = 8)
pyplot.plot(delay_duration, alpha_ion_2, 'ok--', label = 'ion 2', markersize = 8)
# pyplot.plot(delay_duration, alpha_ion_1, 'ob--', label = 'ion 1', markersize = 8)
pyplot.tight_layout()
pyplot.title('Pulsed Heating Delay', fontsize = 32)
pyplot.xlabel('Delay ($\\mu s$)', fontsize = 26)
pyplot.ylabel(u'Displacement $|\\alpha|$', fontsize = 26)
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.legend(prop={'size':22})
pyplot.xscale('log')
# pyplot.savefig('together_delay.png')
pyplot.show()