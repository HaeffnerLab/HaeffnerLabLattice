import numpy as np
import numpy
import timeit



def cartesian_product(arrays):
    broadcastable = numpy.ix_(*arrays)
    print broadcastable
    broadcasted = numpy.broadcast_arrays(*broadcastable)
    rows, cols = reduce(numpy.multiply, broadcasted[0].shape), len(broadcasted)
    out = numpy.empty(rows * cols, dtype=broadcasted[0].dtype)
    start, end = 0, rows
    for a in broadcasted:
        out[start:end] = a.reshape(-1)
        start, end = end, end + rows
    return out.reshape(cols, rows).T
     
# all_combinations = cartesian_product([[0,1] for i in range(5)])
# for j in range(all_combinations):

ion_g = np.array([1,2,3,4])
ion_g2 =np.array([11,12,13,14])
ion_g3 =np.array([12,22,23,24])

ions = np.vstack((ion_g,ion_g2, ion_g3))

def partial_sum(mask = [[True, False, True], [False, False, True]]):
    
#     ion_combinations = np.ones(3)
#     print np.outer(ion_combinations, ions)
#     mask =np.array(mask)
    ion_array = np.tile(ions, (2,1)).reshape(2,3,4)
#     ion_array = np.asarray([ions]*32)
    print ion_array[mask]
#     print cartesian_product(((ions , np.ones_like(ions))))
#     select = np.where(mask)
#     print select
#     print ions[select]
    
print timeit.timeit(partial_sum, number = 1)