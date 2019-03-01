import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
from common.client_config import client_info as cl
from multi_test import multi_test

class multi2d_test2(pulse_sequence):

    is_2dimensional = True
    is_composite = True

    show_params = ['NSY.pi_time']

    scannable_params = {
        'Heating.background_heating_time': [(0., 5000., 500., 'us'), 'current']
              }

    fixed_params = {'StateReadout.ReadoutMode':'pmt'}

    sequence = multi_test

    @classmethod
    def run_finally(cls, cxn, parameter_dct, all_data, data_x):
    	return 0.1


