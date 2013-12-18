'''
python setup.py build_ext --inplace
'''

from simulation import simulator
import numpy as np
from simulation_parameters import simulation_parameters
from equilbrium_positions import equilibrium_positions as equil
from matplotlib import pyplot
import matplotlib
matplotlib.rc('xtick', labelsize=20) 
matplotlib.rc('ytick', labelsize=20) 

p = simulation_parameters()
simulation = simulator(p)

starting_positions = np.zeros((p.number_ions, 3))
starting_velocities = np.zeros((p.number_ions, 3))
starting_positions[:, 0] = p.number_ions * [0]
starting_positions[:, 1] = p.number_ions * [0]
starting_positions[:, 2] = equil.get_positions(p.number_ions, p.f_z, p)
center_ion = p.number_ions / 2 +1
heated_ion = 0
starting_positions[heated_ion, 0] +=10e-9
# starting_velocities[heated_ion, 0] +=1e-9
# starting_positions[heated_ion+1, 0] +=10e-9

positions,excitations = simulation.simulation(starting_positions, starting_velocities, random_seeding = 0)
print positions[0,:,0]
velocities = np.diff(positions, axis = 1) / p.timestep
print 'vel'
time_axis = np.arange(positions.shape[1]) * p.timestep * 10**6
print 't'
energy_left = velocities[0, :, 0]**2 * p.mass * .5 / p.hbar / (2 * np.pi * p.f_x)
print 'eleft'
energy_right = velocities[-1, :, 0]**2 * p.mass * .5 / p.hbar / (2 * np.pi * p.f_x)
print 'eright'
energy_center = velocities[center_ion, :, 0]**2 * p.mass * .5 / p.hbar / (2 * np.pi * p.f_x)
print 'center'

chunksize = 2000
numchunks = energy_left.size // chunksize 
energy_left = energy_left[:chunksize*numchunks].reshape((-1, chunksize))
energy_right = energy_right[:chunksize*numchunks].reshape((-1, chunksize))
energy_center = energy_center[:chunksize*numchunks].reshape((-1, chunksize))
time_axis_binned = time_axis[:chunksize*numchunks].reshape((-1, chunksize))
energy_left = energy_left.mean(axis=1)
energy_right = energy_right.mean(axis=1)
energy_center = energy_center.mean(axis=1)
time_axis_binned = time_axis_binned.mean(axis=1)

print 'done binning'

# pyplot.figure()
# pyplot.plot(time_axis, 10**6 * positions[0, :, 0], label = 'left ion')
# pyplot.plot(time_axis, 10**6 * positions[-1, :, 0], label = 'right ion')
# pyplot.title(r"5 ions, x - kick propagation, f_z = {} KHz".format(p.f_z / 10.**3), fontsize = 30)
# pyplot.xlabel(r'$\mu s$', fontsize = 30)
# pyplot.ylabel(r'Displacement along x, $\mu m$', fontsize = 30)
# pyplot.tick_params(axis='both', labelsize = 20)
# pyplot.xlim(0,2000)
# pyplot.legend(fontsize = 20)

pyplot.figure()
offset = 1
max_energy = energy_left.max()
energy_left = energy_left / max_energy
energy_right = energy_right / max_energy
# energy_center = energy_center / max_energy + 2 * offset
pyplot.subplot(121)
pyplot.plot(time_axis_binned, energy_left, 'b', label = 'left ion')
ymax = 120/114.311895325#making sure y-heights match
pyplot.ylim(0,ymax)
pyplot.xlim(-10, 610)
ax = pyplot.gca()
ax.xaxis.set_ticklabels([0,0,100,200,300,400,500])
pyplot.subplot(122)
pyplot.plot(time_axis_binned, energy_right, 'b', label = 'right ion')
pyplot.xlim(-10, 610)
# pyplot.plot(time_axis_binned, energy_center, 'k', label = 'center ion')
pyplot.ylim(0,ymax)
ax = pyplot.gca()
ax.yaxis.set_ticklabels([])


# np.save('energy_left5ms_5ions', energy_left)


# pyplot.figure()
# freq = np.fft.fftfreq(time_axis_binned.size, chunksize*p.timestep)
# fft = np.fft.fft(energy_left)
# total_fft = np.abs(fft)
# fft = np.fft.fft(energy_right)
# total_fft += np.abs(fft)
#not plotting the DC term, only plotting f>0

# pos_freqs = np.where(freq > 0)
# pyplot.plot(freq[pos_freqs] /10**3, total_fft[pos_freqs])
# pyplot.xlabel('Frequency KHz')
# pyplot.title('FFT', fontsize = 20)

pyplot.tight_layout()
# plot_15()
# plot_25()
fig = pyplot.gcf()
pyplot.subplots_adjust(wspace = 0)
fig.set_size_inches(19.2,5.4)
pyplot.savefig('comparison_theory_bottom.pdf')
pyplot.show()