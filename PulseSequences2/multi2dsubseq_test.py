import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
from common.client_config import client_info as cl
from multi2d_test2 import multi2d_test2
from RabiFlopping import RabiFlopping

class multi2dsubseq_test(pulse_sequence):

    is_2dimensional = True
    is_composite = True

    # scannable_params = {
    #     'Heating.background_heating_time': [(0., 5000., 500., 'us'), 'current']
    #           }

    fixed_params = {'StateReadout.ReadoutMode':'pmt'}

    sequence = [multi2d_test2, RabiFlopping]

    @classmethod
    def run_finally(cls, cxn, parameter_dct, all_data, data_x):
        return 0.1


