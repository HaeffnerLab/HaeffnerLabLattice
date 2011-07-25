# Example python script for pysifreader
from pysifreader import *
import matplotlib
matplotlib.use('Qt4Agg')
from pylab import *

# Read the SIF file
#[data, back, ref] = sifread('image.sif')
#pixels = data.imageData[:,:,0] - back.imageData[:,:,0]


[data, back, ref] = sifread('ourimage2.sif')
pixels =  data.imageData[:,:,0]
print type(pixels)
# Print some information about the main (data) image
data.printInfo()

# Display the image
matshow(log(pixels))
show()