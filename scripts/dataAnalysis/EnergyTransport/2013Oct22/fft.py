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
        
t = np.array(merged[0])
# ion_data = merged[1]
# pyplot.subplot(211)
# pyplot.plot(t, ion_data)
pyplot.subplot(111)
total_fft = 0
freq = np.fft.fftfreq(t.size, 20e-6)
for i in range(1,6):
    ion_data = merged[i]
    fft = np.fft.fft(ion_data)
    total_fft += np.abs(fft)
#not plotting the DC term, only plotting f>0

pos_freqs = np.where(freq > 0)
pyplot.plot(freq[pos_freqs] /10**3, total_fft[pos_freqs])
pyplot.xlabel('Frequency KHz')
pyplot.title('FFT', fontsize = 20)
pyplot.savefig('fft.png', dpi = 150)
pyplot.show()
# pyplot.ylim([0,3])
# pyplot.xlabel(r'Delay after heat $\mu s$', fontsize = 26)
# pyplot.ylabel('Excitation (arb)', fontsize = 26)
# pyplot.tick_params(axis='both', which='major', labelsize=20)
# pyplot.legend()
# fig = pyplot.gcf()
# fig.set_size_inches(12,8)

# pyplot.tight_layout()
# pyplot.show()
