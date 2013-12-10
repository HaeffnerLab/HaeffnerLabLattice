import labrad
from matplotlib import pyplot
import numpy as np
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

figure = pyplot.figure()
figure.clf()


datasets  = [
             ('2013Oct21','1837_52'),
             ('2013Oct21','1855_28'),
             ]


merged = {}
for day,name in datasets:
    dv.cd(['','Experiments','Blue Heat ScanDelay',day,name])
    dv.open(1)
    data = dv.get().asarray
    for i in range(data.shape[1]):
        current = merged.get(i, [])
        current.extend(data[:,i])
        merged[i] = current
        
offset = 0.5

t = merged[0]

colors = [
          (1, 'b', 0),
          (2, 'g', 1),
          (3, 'k', 2),
          (4, 'm', 3),
          (5, 'r', 4),
          ]

for ion,color,order in colors:
    ion_data = np.array(merged[ion]) + order * offset
    pyplot.plot(t, ion_data,'o-', color = color, label = 'ion {}'.format(ion-1))

pyplot.title('Energy Transport, 5 ions', fontsize = 32)
pyplot.ylim([0,3])
pyplot.xlabel(r'Delay after heat $\mu s$', fontsize = 26)
pyplot.ylabel('Excitation (arb)', fontsize = 26)
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.legend()
fig = pyplot.gcf()
fig.set_size_inches(12,8)
pyplot.savefig('all_ions.png', dpi = 150)
# pyplot.tight_layout()
pyplot.show()
