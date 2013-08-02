import labrad
from matplotlib import pyplot
import numpy as np

info = [('2013Jul30', '1637_53')]

cxn = labrad.connect()
dv = cxn.data_vault

for date, datasetName in info:
    dv.cd( ['','Experiments','RabiFlopping',date,datasetName])
    dv.open(1)
    data = dv.get().asarray
    transpose = data.transpose()
    times = transpose[0]
    flops = transpose[1:]
    x = flops[-2]
    y = flops[-1]
    
#see Pearson product-moment correlation coefficient
def find_r(x, y):
    numerator = np.sum((x - x.mean()) * (y - y.mean()))
    denominator = np.sqrt(np.sum((x - x.mean())**2) * np.sqrt(np.sum((y - y.mean())**2)))
    r = numerator / denominator
    return r


r_random_permute = []
for i in range(10000):
    random_x = x[np.random.permutation(x.size)]
    r_random_permute.append( find_r(x, random_x) )
r_random_permute = np.array(r_random_permute)

r_data = find_r(x,y)
binned,bins,edges =pyplot.hist(r_random_permute, 50)
pyplot.vlines(r_data, binned.min(), binned.max(), 'r')
pyplot.xlim([-1,1])
pyplot.show()