import matplotlib

from matplotlib import pyplot
import numpy as np

size=1.5

figure = pyplot.figure()

label = r'$\Omega t$'

points = ['piover4','piover2','3piover4','pi','3piover2','2pi']#,'5piover4'
colors = ['r','b','y','g','k','m']

fig=[]
i=0
print 'loading doppler data ...'
for folder in points:
    print 'file {}'.format(folder)
    if folder == '2pi':
        fig.append(pyplot.figure(figsize=(18, 4.6)))
        pyplot.xticks((0,np.pi/2,np.pi,3.0*np.pi/2,2.0*np.pi),(0,r'$\frac{\pi}{2}$',r'$\pi$',r'$\frac{3\pi}{2}$',r'$2\pi$'))
        fig[i].subplots_adjust(left=0.05, right=0.975, bottom=0.2, top=0.9)
#        pyplot.xlabel('Subsequent evolution '+r'$\Omega t$',fontsize=22)
    else:
        fig.append(pyplot.figure(figsize=(18, 4)))
        pyplot.xticks((0,np.pi/2,np.pi,3.0*np.pi/2,2.0*np.pi),())
        fig[i].subplots_adjust(left=0.05, right=0.975, bottom=0.1, top=0.9)
#    col = colors[i]
    fig[i].canvas.set_window_title(folder)
    pyplot.grid(True, 'major')
    col = 'k'
    dist_x_data = np.loadtxt('data/'+folder+'/dist_x_data.txt')
    dist_y_data = np.loadtxt('data/'+folder+'/dist_y_data.txt')
    dist_y_data_errs = np.loadtxt('data/'+folder+'/dist_y_data_errs.txt')
    dist_x_theory = np.loadtxt('data/'+folder+'/dist_x_theory.txt')
    dist_y_theory = np.loadtxt('data/'+folder+'/dist_y_theory.txt')
#    pyplot.plot(dist_x_data,dist_y_data)
    parameter = np.loadtxt('data/'+folder+'/parameter.txt')
    eta=parameter[7]
#    pyplot.plot(dist_x_data,dist_y_data)
    pyplot.errorbar(eta*2.0*np.pi*dist_x_data,dist_y_data,yerr=dist_y_data_errs,xerr=0,fmt='o',color=col,mew=3,capsize=5,ms=8)
    pyplot.plot(eta*2.0*np.pi*dist_x_theory,dist_y_theory,'-',color=col)
#    pyplot.xlabel(r'Excitation time '+label,fontsize=size*22)
    pyplot.ylim((0,0.25))
    pyplot.yticks((0,0.1,0.2))
    pyplot.xlim((0,1.3*np.pi))
#    pyplot.title('Open-System Hilbert-Schmidt distance',fontsize=size*30)
    pyplot.tick_params(axis='x', labelsize=size*22)
    pyplot.tick_params(axis='y', labelsize=size*22)
    pyplot.savefig('pdf/doppler_'+folder+'.pdf')
    i+=1
print '... done'

#pyplot.ylabel('Operator Distance')
#pyplot.legend()

#pyplot.legend(loc=2,prop={'size':size*15})
#pyplot.xticks([np.pi/4.0,3.0*np.pi/4.0,np.pi/2.0,np.pi,5.0*np.pi/4.0,3.0*np.pi/2.0],[r'$\frac{\pi}{4}$',r'$\frac{3\pi}{4}$',r'$\frac{\pi}{2}$',r'$\pi$',r'$\frac{5\pi}{4}$',r'$\frac{3\pi}{2}$'])
#print 'parameters:\n nbar = {} \n trap frequency = {}'.format(nbar,trap_frequency)
pyplot.show()