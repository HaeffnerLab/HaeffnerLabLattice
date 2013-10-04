import labrad
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

freq_shift = 25.283

dv.cd(['','Experiments','Blue Heat Spectrum','2013Oct02','1454_43'])
dv.open(1)
data = dv.get().asarray
x,y = data.transpose()
figure = pyplot.figure()
pyplot.plot(1000*(x + freq_shift), y,'o-', label = 'no heating')

dv.cd(['','Experiments','Blue Heat Spectrum','2013Oct02','1456_40'])
dv.open(1)
data = dv.get().asarray
x,y = data.transpose()

pyplot.plot(1000*(x + freq_shift), y,'or-', label = 'heating 40mus')

pyplot.title('Sideband spectrum', fontsize = 32)
pyplot.xlabel(r'Frequency KHz', fontsize = 20)
pyplot.ylabel('Excitation percentage', fontsize = 20)
pyplot.tick_params(axis='both', which='major', labelsize=16)
pyplot.legend()
pyplot.xticks([-100,-80,-60,-40,-20,0,20,40,60,80,100])
pyplot.xlim([-100,100])
pyplot.ylim([0,1])
pyplot.savefig('spectrum_shift.png')
# pyplot.show()
