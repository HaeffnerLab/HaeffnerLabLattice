'''
python setup.py build_ext --inplace
'''

import hello

import time
t = time.time()
output = hello.verlet_step()
print time.time() - t