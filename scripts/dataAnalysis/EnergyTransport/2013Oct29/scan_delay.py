import labrad
from matplotlib import pyplot
import numpy as np
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

figure = pyplot.figure()
figure.clf()


datasets  = [
             ('2013Oct30','1746_13','b',0),
             ('2013Oct30','1823_07','r',14),
             ]


merged = {}
for day,name,color,ion in datasets:
    dv.cd(['','Experiments','Blue Heat ScanDelay',day,name])
    dv.open(1)
    data = dv.get().asarray
    t,ion_data = data.transpose()
    pyplot.plot(t, ion_data,'o-', color = color, label = 'ion {}'.format(ion))
 

pyplot.title('Energy Transport, 15 ions', fontsize = 32)
pyplot.ylim([0,1])
pyplot.xlabel(r'Delay after heat $\mu s$', fontsize = 26)
pyplot.ylabel('Excitation (arb)', fontsize = 26)
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.legend()
fig = pyplot.gcf()
fig.set_size_inches(12,8)
pyplot.savefig('all_ions.png', dpi = 150)
import os
print os.getcwd()
# pyplot.tight_layout()
# pyplot.show()
