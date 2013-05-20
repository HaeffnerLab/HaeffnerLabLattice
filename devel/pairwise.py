#import numpy as np
#
#
#detuning_para = 0.0
#
#detuning = detuning_para*1.319E8
#
#s = 1.0
#laser_direction_temp = np.array([1.0,1.0,0.0])
#
#laser_direction = laser_direction_temp/np.sqrt(np.sum(laser_direction_temp**2))
#
#recoil_velocity = 0.024877240126316254*laser_direction
#k_laser = (np.pi*2.0/(397E-9))*laser_direction 
#
#data_1 = [1.0, 1.0, 1.0]
#
#doppler = np.inner(k_laser,data_1)
#gamma = 1.319E8
#rho_ee = s*0.5/(1+s+(2*(detuning+doppler)/gamma)**2.0)
#
#print rho_ee
import numpy as np
from matplotlib import pyplot
data = np.loadtxt('/home/lattice/Simulation/trajectories')
x = np.arange(len(data))
figure = pyplot.figure()
pyplot.plot(x, data)
pyplot.show()