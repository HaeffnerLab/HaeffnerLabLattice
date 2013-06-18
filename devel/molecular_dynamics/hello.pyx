import labrad.units as U
from simulation_parameters import simulation_parameters as p
from libc.math cimport sin
from cython.view cimport array as cvarray
import numpy as np

cdef int TOTAL_STEPS = p.total_steps
cdef int NUMBER_IONS = p.number_ions

cdef void acceleration(double [:] position, double [:] current_acceleration):
    '''
    given the current position, computes the current acceleration and fills in the current_acceleration array
    '''
    cdef int i = 0
    for i in range(NUMBER_IONS):
        current_acceleration[i] = 1

cdef void acceleration_test(double [:] initial_position, double [:] initial_acceleration, double [:, :] positions):
    current_position = initial_position
    current_acceleration = initial_acceleration
    cdef int i
    cdef double next_print_progress = 1
    for i in range(TOTAL_STEPS):
        if next_print_progress / 100.0 < float(i) / TOTAL_STEPS:
            print 'PROGRESS: {} %'.format(next_print_progress)
            next_print_progress = next_print_progress + 1
        acceleration(current_position, current_acceleration)
        positions[0,i] = i
#         arr[1,i] = 2 * i
    
def verlet_step():
    positions = np.empty((NUMBER_IONS, TOTAL_STEPS))
    current_position = np.empty(NUMBER_IONS)
    current_acceleration = np.empty(NUMBER_IONS)
    cdef double [:] current_position_view = current_position
    cdef double [:, :] positions_view = positions
    cdef double [:] current_acceleration_view = current_acceleration
    acceleration_test(current_position_view, current_acceleration_view, positions_view)