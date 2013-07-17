import numpy as np
import matplotlib
#from constants import constants as c

from matplotlib import pyplot

#calculate magnetic field from a coil with length L, radii r1 and r2 and at a position z away from the coil front

def hanle(gamma,theta,phi, x):
    signal = (1/gamma)*(1+np.cos(theta))+np.sin(theta)*(gamma*np.cos(phi)-x*np.sin(phi))/(gamma**2+x**2)
    return signal

theta = np.pi/2

x1 = np.arange(-60,0,0.01)

# pyplot.plot(x1,hanle(22,theta,np.pi*(0.5),x1))
# pyplot.plot(x1,hanle(22,theta,np.pi*(0.5+0.01),x1))
# pyplot.plot(x1,hanle(22,theta,np.pi*(0.5+0.02),x1))
# pyplot.plot(x1,hanle(22,theta,np.pi*(0.5+0.03),x1))
# pyplot.plot(x1,hanle(22,theta,np.pi*(0.5+0.04),x1))
# pyplot.plot(x1,hanle(22,theta,np.pi*(0.5+0.05),x1))

x2 = np.arange(60,0,-0.01)

# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5),x2))
# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5+0.01),x2))
# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5+0.02),x2))
# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5+0.03),x2))
# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5+0.04),x2))
# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5+0.05),x2))

# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5),x2)-hanle(22,theta,np.pi*(0.5),x1))
# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5+0.01),x2)-hanle(22,theta,np.pi*(0.5+0.01),x1))
# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5+0.02),x2)-hanle(22,theta,np.pi*(0.5+0.02),x1))
# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5+0.03),x2)-hanle(22,theta,np.pi*(0.5+0.03),x1))
# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5+0.10),x2)-hanle(22,theta,np.pi*(0.5+0.10),x1))
# pyplot.plot(x2,hanle(22,theta,np.pi*(0.5+0.15),x2)-hanle(22,theta,np.pi*(0.5+0.15),x1))

pyplot.plot(x2,hanle(22,theta*(1.001),np.pi*(0.5+0.15),x2)-hanle(22,theta*(1.001),np.pi*(0.5+0.15),x1))
pyplot.plot(x2,hanle(22,theta*(1.01),np.pi*(0.5+0.15),x2)-hanle(22,theta*(1.01),np.pi*(0.5+0.15),x1))
pyplot.plot(x2,hanle(22,theta*(1.015),np.pi*(0.5+0.15),x2)-hanle(22,theta*(1.015),np.pi*(0.5+0.15),x1))
pyplot.plot(x2,hanle(22,theta*(1.02),np.pi*(0.5+0.15),x2)-hanle(22,theta*(1.02),np.pi*(0.5+0.15),x1))
pyplot.plot(x2,hanle(22,theta*(1.025),np.pi*(0.5+0.15),x2)-hanle(22,theta*(1.025),np.pi*(0.5+0.15),x1))

pyplot.show()