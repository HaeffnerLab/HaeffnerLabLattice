import qutip
import numpy as np
from numpy import cos, sin

# b = qutip.Bloch()
# b.frame_color = 'grey'
# init_vector = [-0.75, 0.25, 0.5]
# 
# b.add_vectors(init_vector)
# 
# 
# b.show()

b = qutip.Bloch()
b.point_color = ['g'] 
b.frame_color = 'grey'
x0 = -0.5; y0 = 0.7; z0 = 0.5
init_vector = [x0, y0, z0]
final_vector = [x0, -z0, y0]

pts = 30
xp = [x0] * pts
yp = [y0 * cos(theta) + sin(theta) * -z0 for theta in np.linspace(0, np.pi/2, pts)]
zp = [z0 * cos(theta) + sin(theta) * y0 for theta in np.linspace(0, np.pi/2, pts)]
# b.add_points([xp, yp, zp])

b.add_vectors(init_vector)
# b.add_vectors(final_vector)

# b.add_vectors([init_vector, final_vector])
  
  
b.show()

