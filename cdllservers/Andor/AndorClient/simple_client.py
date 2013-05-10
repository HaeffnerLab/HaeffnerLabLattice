import labrad
from labrad.units import WithUnit
import numpy as np

# cxn = labrad.connect()
# cam = cxn.andor_server
# 
# print 'setting exposure time'
# cam.set_exposure_time(WithUnit(0.1,'s'))

# print data.max(), data.min()
# import matplotlib
# matplotlib.use('Qt4Agg')
# from matplotlib import pyplot
# pyplot.imshow(data)
# pyplot.show()
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph
app = QtGui.QApplication([])

win = pyqtgraph.GraphicsLayoutWidget()
view = win.addViewBox()
# view.setRange(QtCore.QRectF(0, 0, 600, 600))
img = pyqtgraph.ImageItem()
view.addItem(img)
# win.show()
# imv = pyqtgraph.ImageItem(border = 'w')


# def update_plot():
# 
#     cam.start_acquisition()
#     print 'waiting for acquistion to complete'
#     cam.wait_for_acquisition()
#     print 'DONE'
# #     import time
# #     print time.time()
#     data = cam.get_acquired_data().asarray
#     binx,biny, startx, stopx, starty, stopy = cam.get_image_region()
#     pixels_x = (stopx - startx + 1) / binx
#     pixels_y = (stopy - starty + 1) / biny
#     image_data = np.reshape(data, (pixels_x, pixels_y))
#     
#     img.setImage(image_data)
#     QtCore.QTimer.singleShot(1, update_plot)
    
# # imv.getRoiPlot()
# imv.getHistogramWidget()
# win.addPlot(imv)
# win.show()

# update_plot()


if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()