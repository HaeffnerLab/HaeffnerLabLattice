import labrad
import numpy as np
import matplotlib

from matplotlib import pyplot
from scipy.optimize import curve_fit
from scipy.stats import chi2

#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault
#change directory
directory = ('2012Dec20','2158_40')
dv.cd(['','Experiments','729Experiments','Spectrum',directory[0],directory[1]])
dv.open(1)
data = dv.get().asarray
#get parameters
line = dv.get_parameter('spectrum_saved_frequency')
excitation_time = dv.get_parameter('excitation_time')[2]['us']

freqs = 2 * 1000 * data[:,0] #frequency in real KHz
probs = data[:,1]
trials = 100

def errorBarSimple(trials, prob):
    #look at wiki http://en.wikipedia.org/wiki/Checking_whether_a_coin_is_fair
    '''returns 1 sigma error bar on each side i.e 1 sigma interval is val - err < val + err'''
    Z = 1.0
    s = np.sqrt(prob * (1.0 - prob) / float(trials))
    err = Z * s
    return err

err = errorBarSimple(trials, probs)

n = len(freqs) # the number of data points
p0 = [453177.0, 0.5, 0.5] # initial values of parameters

def lorentzian(w, center, linewidth, area):
    '''
    lorentzian function
    @param center: center of the function
    @param param:  linewidth \Gamma
    @param area: total area under the function (1.0 for normalized)
    '''
    return (area / np.pi) * (linewidth / 2.0)**2 / ( ((linewidth / 2.0)**2) + (w - center)**2  )

p, covm = curve_fit(lorentzian, freqs, probs, p0, err) # do the fit
center, linewidth , area = p


chisq = sum(((lorentzian(freqs, center, linewidth, area) - probs) / err)**2) # compute the chi-squared
ndf = n -len(p) # no. of degrees of freedom
Q = 1. - chi2.cdf(chisq, ndf) # compute the quality of fit parameter Q
chisq = chisq / ndf # compute chi-squared per DOF
x_0_err,b_err,a_err = np.sqrt(np.diag(covm)/chisq) # correct the error bars

#make plot
centered_freqs = freqs - center
figure = pyplot.figure()


pyplot.errorbar(centered_freqs, probs, yerr = np.vstack((err,err)), fmt = 'ko')

x_fit = np.linspace(4 * centered_freqs.min(), 4*centered_freqs.max(), 5000)
pyplot.plot(x_fit, lorentzian(x_fit + center, center ,linewidth , area),'r-',linewidth=3.0)
text = r'$\Gamma$ = {0:.2f} kHz'.format(linewidth) + '\n'
text+= 'Experiment {0}, {1}\n'.format(*directory)
text+= 'Transition {0}\n'.format(line)
text+= r'Excition time = {0} $\mu s$'.format(excitation_time)

pyplot.annotate(text, xy=(0.7, 0.9), xycoords='axes fraction',fontsize=15)
pyplot.xlabel( 'Frequency (kHz)',fontsize=15)
pyplot.ylabel('Excitation probability',fontsize=15)
pyplot.title('Excitation spectrum of 729 nm transition',fontsize=20)
pyplot.ylim([0,1.0])
pyplot.xlim([-1.5,1.5])
pyplot.show()