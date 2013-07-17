import numpy as np

#calculate magnetic field from a coil with length L, radii r1 and r2 and at a position z away from the coil front

z = 0.11
L = 0.1524
r1 = 0.01905
r2 = 0.04445
I = 657*20
k = 6.28318531e-7
loop_integral = (z+L)*np.log2((np.sqrt(r2**2+(z+L)**2)+r2)/(np.sqrt(r1**2+(z+L)**2)+r1))-z*np.log2((np.sqrt(r2**2+(z)**2)+r2)/(np.sqrt(r1**2+(z)**2)+r1))
B = 10000*k*loop_integral*I/(L*(r2-r1))

print "Magnetic field is", B, "gauss."