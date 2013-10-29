from matplotlib import pyplot
import numpy as np

frist_sideband_data = np.array([
                   [0, 0], #extracted nbar = 3.4 from 1821_02, 2_pi_time of 8.4 \mus set by 1822_17
                   [10, 5.5], #1905_04
                   [30, 14.1], #1905_47
                   [50, 34.1],  #1906_36
                   [70, 40], #1907_20
                   [90, 56], #1908_05
                   ])

second_sideband_data = np.array([
                   [0, 0], #extracted nbar = 3.4 from 1821_02, 2_pi_time of 8.4 \mus set by 1822_17
                   [10, 5.7], #1914_14
                   [30, 16], #1915_02
                   [50, 25.9],  #1915_46
                   [70, 49.6], #1916_36
                   ])

pulsed_heating_duration, alpha = frist_sideband_data.transpose()
pyplot.plot(pulsed_heating_duration, alpha, 'or--', label = 'first sideband', markersize = 8)

pulsed_heating_duration, alpha = second_sideband_data.transpose()
pyplot.plot(pulsed_heating_duration, alpha, 'ob--', label = 'second sideband', markersize = 8)



# pyplot.tight_layout()
pyplot.title('Pulsed Heating Displacement', fontsize = 32)
pyplot.xlabel('Pulsed Heating Time ($\\mu s$)', fontsize = 26)
pyplot.ylabel(u'Displacement $|\\alpha|$', fontsize = 26)
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.legend(prop={'size':22}, loc = 'lower right')
yticks = pyplot.yticks()[0]
alpha_sq_axis = pyplot.twinx()
alpha_sq_axis.tick_params(axis='both', which='major', labelsize=20)
alpha_sq_axis.set_yticks(yticks)
alpha_sq_axis.set_yticklabels([int(t)**2 for t in yticks])
alpha_sq_axis.set_ylabel(u'$|\\alpha|^2$', fontsize = 26)
fig = pyplot.gcf()
fig.set_size_inches(12,8)
pyplot.savefig('together_heating.png')
pyplot.show()