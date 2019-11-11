from matplotlib import pyplot
import numpy as np

def plot_FM(alpha,spins_list,fm_str,kT=0,pts = 200,t_res = 200,t_max=10):
    for number_of_spins in spins_list:
        B_list,max_distances,total_trace_distance = np.load(fm_str+'/trd_spins_{}_pts_{}_t_res_{}_t_max_{}_alpha_{}_kT_{}.npy'.format(number_of_spins,pts,t_res,t_max,alpha,kT))
        pyplot.plot(B_list,max_distances,label = '{} spins, kT={}'.format(number_of_spins,kT))
        pyplot.plot(B_list,total_trace_distance,label = '{} spins, kT={}'.format(number_of_spins,kT))
        print number_of_spins
    pyplot.xscale('log')
    pyplot.legend()

fm_str = 'FM'
alpha = 1.0
spins_list = range(2,3)
# plot_FM(alpha,spins_list,fm_str)
# plot_FM(alpha,spins_list,fm_str,t_max=1000,kT=0.0001)
# plot_FM(alpha,spins_list,fm_str,kT=0.0005)
# plot_FM(alpha,spins_list,fm_str,kT=0.001)
# plot_FM(alpha,spins_list,fm_str,kT=0.01)
# plot_FM(alpha,spins_list,fm_str,kT=0.1)
plot_FM(alpha,spins_list,fm_str,kT=1.0)
pyplot.show()