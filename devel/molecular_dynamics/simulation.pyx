import labrad.units as U
from simulation_parameters import simulation_parameters as p
from libc.math cimport sin
from cython.view cimport array as cvarray
import numpy as np

cdef int TOTAL_STEPS = p.total_steps
cdef int NUMBER_IONS = p.number_ions
cdef double TIMESTEP = p.timestep

cdef void calculate_acceleration(double [:, :] position, double [:, :] current_acceleration):
    '''
    given the current position, computes the current acceleration and fills in the current_acceleration array
    '''
    cdef int i = 0
    for i in range(NUMBER_IONS):
        current_acceleration[i, 0] = i
        current_acceleration[i, 1] = i
        current_acceleration[i, 2] = i

cdef void do_verlet_integration(double [:, :] initial_position, double [:, :, :] positions):
    current_position = initial_position
    cdef double[:, :] current_acceleration = initial_position
    cdef int i
    cdef int j
    cdef int k
    cdef double next_print_progress = 1
    for i in range(2, TOTAL_STEPS):
        #print progress update
        if next_print_progress / 100.0 < float(i) / TOTAL_STEPS:
            print 'PROGRESS: {} %'.format(next_print_progress)
            next_print_progress = next_print_progress + 1
        calculate_acceleration(current_position, current_acceleration)
        #cycle over ions
        for j in range(NUMBER_IONS):
            #cycle over coordinates
            for k in range(3):
                positions[j, i, k] = 2 * positions[j , i - 1, k] -  positions[j, i - 2, k] + current_acceleration[j, k]
    
def verlet_step():
    positions = np.empty((NUMBER_IONS, TOTAL_STEPS, 3))
    current_position = np.empty((NUMBER_IONS, 3))
    cdef double [:, :] current_position_view = current_position
    cdef double [:, :, :] positions_view = positions
#     cdef double [:, :] current_acceleration_view = current_acceleration
    do_verlet_integration(current_position_view, positions_view)