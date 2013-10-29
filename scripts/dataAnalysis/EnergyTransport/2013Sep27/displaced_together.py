from matplotlib import pyplot
import numpy as np

high_power_data = np.array([
                   [0, 0], #extracted nbar = 3.4 from 1821_02, 2_pi_time of 8.4 \mus set by 1822_17
                   [10, 3.5], #1905_04
                   [40, 9.4], #1905_47
                   [70, 15],  #1906_36
                   [100,10.6], #1907_20
                   [130, 3.43], #1908_05
                   [160, 2.1], #1908_54
                   [190, 5.3], #1909_38
                   [220, 5.4], #1910_22
                   [250, 4.5], #1911_12
                   ])

lower_power_data = np.array([
                   [0, 0], #extracted nbar = 3.4 from 1821_02, 2_pi_time of 8.4 \mus set by 1822_17
                   [10, 2.3], #1914_14
                   [40, 5.4], #1915_02
                   [70, 7.7],  #1915_46
                   [100,11.4], #1916_36
                   [130, 12.7], #1917_20
                   [160, 14.7], #1918_04
                   [190, 13.8], #1918_54
                   [220, 13.4], #1919_38
                   [250, 11.0], #1920_22
                   [280, 10.3], #1921_12
                   [310, 9.5], #1921_56
                   [340, 5.1], #1922_45
                   [370, 3.3], #1923_30
                   [400, 1.4], #1924_14
                   [450, 3.1], #1925_22
                   ])

pulsed_heating_duration, alpha = high_power_data.transpose()
pyplot.plot(pulsed_heating_duration, alpha, 'or--', label = '-12 dBm heating', markersize = 8)

pulsed_heating_duration, alpha = lower_power_data.transpose()
pyplot.plot(pulsed_heating_duration, alpha, 'ob--', label = '-18 dBm heating', markersize = 8)



# pyplot.tight_layout()
pyplot.title('Pulsed Heating Displacement', fontsize = 32)
pyplot.xlabel('Pulsed Heating Time ($\\mu s$)', fontsize = 26)
pyplot.ylabel(u'Displacement $|\\alpha|$', fontsize = 26)
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.legend(prop={'size':22})
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