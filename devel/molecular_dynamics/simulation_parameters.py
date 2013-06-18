from __future__ import division
import numpy as np


class simulation_parameters(object):
    
    number_ions = 5
    ion_amu_mass = 40
    #trap frequencies
    f_drve = 30 * 10**6#Hz
    f_x = 3.1 * 10**6#Hz
    f_y = 2.9 * 10**6#Hz
    f_z = 0.3 * 10**6#Hz
    
    simulation_duration = 0.300#seconds
    timestep = (1 / f_drve) /100#seconds
    total_steps = int(simulation_duration / timestep)