import labrad
import numpy as np

cxn = labrad.connect()
min = cxn.minimal_server

arr = [1, 2, 3, 4, 5, 6]
arr2 = np.reshape(arr, (2, 3))
print arr2

print min.echo(arr2)