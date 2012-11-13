from PyQt4 import QtGui, QtCore

import matplotlib, numpy, sympy
from scipy.optimize import curve_fit
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages

from twisted.internet.defer import inlineCallbacks, returnValue

from labradclient import getID
from config import ConfigDialog, Map
from grapher import formatDSName, formatPath, getSympyFunc, MAP, COLUMN, XAXIS, YAXIS, XPLOT, YPLOT

from fitter import FitDialog

colors = ( 'blue',
           'red',
           'green',
           'cadetblue',
           'orange' )

class Plotter( QtGui.QDialog ):

    lengthChanged = QtCore.pyqtSignal( int )

    class RangeAdjuster( QtGui.QWidget ):
        def __init__( self, parent ):
            super( Plotter.RangeAdjuster, self ).__init__( parent )
            QtGui.QVBoxLayout( self )
            self.slider = QtGui.QSlider( QtCore.Qt.Horizontal, self )
            self.checkBox = QtGui.QCheckBox( self )
            self.checkBox.setChecked( False )
            self.layout().addWidget( self.slider )
            self.layout().addWidget( self.checkBox )

    def __init__( self, name, fullPath, dsHandle, parent ):
        super( Plotter, self ).__init__( parent )

        self.setLayout( QtGui.QVBoxLayout() )

        self.layout().addWidget( QtGui.QLabel( '<big><b>%s</b></big>' % formatDSName( name ) ), 0, QtCore.Qt.AlignCenter )
        self.layout().addWidget( QtGui.QLabel( '<b>%s</b>' % formatPath( fullPath ) ), 0, QtCore.Qt.AlignCenter )

        self.dsHandle = dsHandle
        self._tail = 20
        self.range = { 'min':0, 'max': 0 }
        self.following = False
        self.fit = None
        self.fitDialog = None
        self.length = 0

        self.initDefer = self.initGui()

    @inlineCallbacks
    def initGui( self ):
        dsHandle = self.dsHandle

        varTup = yield dsHandle( 'variables' )
        xVars, yVars = [ [ var[0] for var in indOrDep ] for indOrDep in varTup ]
        self.xData = numpy.array( [] ).reshape( 0, len( xVars ) )
        self.yData = numpy.array( [] ).reshape( 0, len( yVars ) )

        config = self.configDialog = ConfigDialog( self, xVars, yVars, dsHandle )
        config.axesChanged.connect( self.newPlotData )
        config.setModal( True )

        params = yield dsHandle( 'get parameters' )
        params = dict( params ) if params is not None else {}
        xConfig, yConfigs = params.get( XPLOT ), params.get( YPLOT )

        def parseAxis( config, sympyVars ):
            if type( config ) is int and config < len( sympyVars ):
                return config
            if type( config ) is tuple:
                foo = getSympyFunc( config[1], sympyVars )
                if foo:
                    return foo
            return None

        listView = config.xList.listView
        tmpSelectionMode = listView.selectionMode()
        listView.setSelectionMode( listView.MultiSelection )
        tmp = parseAxis( xConfig, config.xList.sympyVars )
        if tmp is None: tmp = 0
        if type( tmp ) is int:
            listView.setCurrentIndex( listView.model().index( tmp, 0, QtCore.QModelIndex() ) )
        if callable( tmp ):
            count = listView.model().rowCount()
            listView.model().addAxis( Map( xConfig[0], tmp, xConfig[1] ) )
            listView.setCurrentIndex( listView.model().index( count, 0, QtCore.QModelIndex() ) )
        listView.setSelectionMode( tmpSelectionMode )

        listView = config.yList.listView
        tmpSelectionMode = listView.selectionMode()
        listView.setSelectionMode( listView.MultiSelection )
        if yConfigs is not None:
            for yConfig in yConfigs:
                tmp = parseAxis( yConfig, config.yList.sympyVars )
                if tmp is not None:
                    if type( tmp ) is int:
                        listView.setCurrentIndex( listView.model().index( int, 0, QtCore.QModelIndex() ) )
                    if callable( tmp ):
                        count = listView.model().rowCount()
                        listView.model().addAxis( Map( yConfig[0], tmp, yConfig[1] ) )
                        listView.setCurrentIndex( listView.model().index( count, 0, QtCore.QModelIndex() ) )
        if not listView.selectedIndexes():
            listView.setCurrentIndex( listView.model().index( 0, 0, QtCore.QModelIndex() ) )
        listView.setSelectionMode( tmpSelectionMode )

        self.xPlot = []
        self.yPlotModel = YPlotModel( self )
        self.fitDialog = FitDialog( self.yPlotModel, self )

        self.fig = Figure( ( 5.0, 4.0 ), dpi = 100 )
        self.canvas = FigureCanvas( self.fig )
        self.canvas.setParent( self )
        self.axes = self.fig.add_subplot( 111 )
        mpl_toolbar = NavigationToolbar( self.canvas, self )
        mpl_toolbar.addAction( QtGui.QIcon( 'icons/fit.svg' ), 'Fit Data', self.fitData ).setToolTip( 'Fit curve to data' )
        mpl_toolbar.addAction( QtGui.QIcon( 'icons/removefit.svg' ), 'Remove Fit', self.removeFit ).setToolTip( 'Remove current fit' )
        self.layout().addWidget( self.canvas, 1 )
        self.layout().addWidget( mpl_toolbar )

        editRow = QtGui.QWidget( self )
        editRow.setLayout( QtGui.QHBoxLayout() )

        rangeMin = self.rangeMin = self.RangeAdjuster( self )
        rangeMax = self.rangeMax = self.RangeAdjuster( self )
        sliderMin, checkMin = rangeMin.slider, rangeMin.checkBox
        sliderMax, checkMax = rangeMax.slider, rangeMax.checkBox
        checkMin.setText( 'Anchor min' )
        checkMax.setText( 'Anchor max' )
        sliderMin.valueChanged.connect( sliderMax.setMinimum )
        sliderMax.valueChanged.connect( sliderMin.setMaximum )
        sliderMin.valueChanged.connect( lambda min: self.updateRange( 'min', min ) )
        sliderMax.valueChanged.connect( lambda max: self.updateRange( 'max', max ) )
        self.lengthChanged.connect( lambda length: sliderMax.setMaximum( length ) if not checkMax.isChecked() else None )
        self.lengthChanged.connect( lambda length: sliderMax.setValue( length ) if self.following else None )
        self.lengthChanged.connect( lambda length: sliderMin.setValue( length - self._tail ) if self.following else None )
        checkMin.toggled.connect( lambda checked: sliderMin.setMinimum( sliderMin.value() ) if checked else sliderMin.setMinimum( 0 ) )
        checkMax.toggled.connect( lambda checked: sliderMax.setMaximum( sliderMax.value() ) if checked else sliderMax.setMaximum( self.length ) )

        editRow.layout().addWidget( rangeMin )
        editRow.layout().addWidget( rangeMax )

        following = QtGui.QCheckBox( 'Following', self )
        following.setChecked( False )
        following.toggled.connect( self.followingStateChange )
        tail = self.tail = QtGui.QSpinBox( self )
        tail.setMinimum( 0 )
        tail.setMaximum( 0 )
        tail.valueChanged.connect( self.tailChanged )
        self.lengthChanged.connect( tail.setMaximum )
        editRow.layout().addWidget( following )
        editRow.layout().addWidget( tail )

        editRow.layout().addStretch()

        xVarBox = self.xVarBox = QtGui.QComboBox( self )
        yVarBox = self.yVarBox = QtGui.QComboBox( self )

        editRow.layout().addWidget( xVarBox )
        editRow.layout().addWidget( yVarBox )

        configure = QtGui.QPushButton( "Configure", self )
        configure.clicked.connect( self.configurePlot )
        editRow.layout().addWidget( configure )
        self.layout().addWidget( editRow )

        self.xVarBox.setModel( self.configDialog.xList.listView.model() )
        self.yVarBox.setModel( self.configDialog.yList.listView.model() )

        self.xVarBox.activated.connect( lambda row: self.configDialog.xList.listView.setCurrentIndex( self.configDialog.xList.listView.model().index( row, 0, QtCore.QModelIndex() ) ) )
        self.xVarBox.activated.connect( lambda index: self.newPlotData() )
        self.yVarBox.activated.connect( lambda row: self.configDialog.yList.listView.setCurrentIndex( self.configDialog.yList.listView.model().index( row, 0, QtCore.QModelIndex() ) ) )
        self.yVarBox.activated.connect( lambda index: self.newPlotData() )

        self.newPlotData()
        yield self.newData()
        sliderMax.setValue( self.length )
        newData = getID()
        yield dsHandle( 'signal: data available', newData )
        dsHandle.addListener( lambda msgCon, null: self.newData(), newData )

#        self.autoFit = QtGui.QCheckBox( self )
#        QtGui.QLabel( "Different Scales", self )

    def saveToPdf( self ):
        pp = PdfPages( 'multipage.pdf' )
        self.fig.savefig( pp, format = 'pdf' )
        pp.close()

    def followingStateChange( self, checked ):
        self.following = checked
        self.rangeMin.setEnabled( not checked )
        self.rangeMax.setEnabled( not checked )
        if checked:
            self.rangeMax.slider.setValue( self.length )
            self.rangeMin.slider.setValue( self.length - self._tail )

    def tailChanged( self, newTail ):
        self._tail = newTail
        if self.following:
            self.rangeMin.slider.setValue( self.length - newTail )

    def newPlotData( self ):
        xIndex = self.configDialog.xList.listView.currentIndex()
        self.xVarBox.setCurrentIndex( xIndex.row() )
        yIndexes = ( self.configDialog.yList.listView.selectedIndexes() )
        self.yVarBox.setEnabled( len( yIndexes ) is 1 )
        if len( yIndexes ) is 1:
            self.yVarBox.setCurrentIndex( yIndexes[0].row() )

        xAxis = self.configDialog.xList.listView.model().axes[xIndex.row()]
        yAxes = [self.configDialog.yList.listView.model().axes[index.row()] for index in yIndexes]
        xArray = self.getCol( xAxis.data, self.xData )
        yArrays = [self.getCol( axis.data, self.yData ) for axis in yAxes]
        xArray, yArrays = self.plotSort( xArray, yArrays )
        self.xPlot = Plot( xArray, xAxis, None )
        self.yPlotModel.clearYPlots()
        for axis, array in zip( yAxes, yArrays ): self.yPlotModel.addYPlot( array, axis )
        self.plot()

    def plotSort( self, x, y ):
        argOrder = x.argsort()
        return x[argOrder], [axis[argOrder] for axis in y]

    def getCol( self, axis, data ):
        if callable( axis ):
            return axis( *data.transpose() )
        else:
            return data[:, axis]

    @inlineCallbacks
    def newData( self ):
        data = yield self.dsHandle( 'get' )
        data = data.asarray
        if not data.any(): return
        xData, yData = data[:, :self.xData.shape[1] ], data[:, self.xData.shape[1] :]
        self.xData = numpy.vstack( ( self.xData, xData ) )
        self.yData = numpy.vstack( ( self.yData, yData ) )
        xNewArrays = self.getCol( self.xPlot.axis.data, xData )
        yNewArrays = [self.getCol( plot.axis.data, yData ) for plot in self.yPlots]
        self.updatePlot( xNewArrays, yNewArrays )
        length = self.xData.shape[0]
        self.length = length

    def updatePlot( self, xNewArray, yNewArrays ):
        xArray = self.xPlot.array
        yArrays = [plot.array for plot in self.yPlots]
        if not xArray.any() or xNewArray.min() <= xArray[-1]:
            xArray, yArrays = self.plotSort( numpy.hstack( ( xArray, xNewArray ) ), [numpy.hstack( ( yOldArray, yNewArray ) ) for yOldArray, yNewArray in zip( yArrays, yNewArrays )] )
        else:
            xNewSorted, yNewSorteds = self.plotSort( xNewArray, yNewArrays )
            xArray = numpy.hstack( ( xArray, xNewSorted ) )
            yArrays = [numpy.hstack( ( yOldArray, yNewSorted ) ) for yOldArray, yNewSorted in zip( yArrays, yNewSorteds )]
        self.xPlot.array = xArray
        for yPlot, yArray in zip( self.yPlots, yArrays ):
            yPlot.array = yArray

    def configurePlot( self ):
        self.configDialog.show()

    def plot( self ):
        self.axes.cla()
        min, max = self.range['min'], self.range['max']
        self.axes.set_xlabel( self.xPlot.axis.name )
        for plot in self.yPlots:
            self.axes.plot( self.xPlot.array[min:max],
                            plot.array[min:max],
                            label = plot.axis.name,
                            color = plot.color,
                            marker = '.',
                            linestyle = 'None' )
        if self.fit is not None:
            fitData, fitParams, fitInfo, fitPlot = self.fit
            self.axes.plot( fitData[0],
                           fitData[1],
                           label = '%s fit for %s' % ( fitInfo.name, fitPlot.axis.name ),
                           color = fitPlot.color,
                           marker = 'None',
                           linestyle = '-',
                           linewidth = 2.0 )
            self.axes.text( .05,
                            .95,
                            'Fit data:\n' + '\n'.join( '%s: %.3f' % ( key, value ) for key, value in zip( fitInfo.params, fitParams ) ),
                            bbox = {'alpha':0.5, 'facecolor':'white'},
                            transform = self.axes.transAxes,
                            ha = 'left',
                            va = 'top' )
        self.axes.legend()
        self.canvas.draw()

    def updateRange( self, key, value ):
        self.range[key] = value
        self.plot()

    def fitData( self ):
        fitDialog = self.fitDialog
        if not fitDialog.exec_(): return
        plot = self.yPlots[fitDialog.plotList.currentIndex()]
        fit = fitDialog.fitList.model().fits[fitDialog.fitList.currentIndex()]
        xArray = self.xPlot.array
        if not xArray.any(): return
        yArray = plot.array
        min, max = self.range['min'], self.range['max']
        x, y = xArray[min:max], yArray[min:max]
        if fit.autofit is None or not fitDialog.checkBox.isChecked():
            guesses = []
            for param in fit.params:
                guess, result = QtGui.QInputDialog.getDouble( self, 'Fit guesses', 'Enter guess for %s:' % param, decimals = 5 )
                if not result:
                    return
                guesses.append( guess )
        else:
            guesses = fit.autofit( x, y )
        params, error = curve_fit( fit.function, x, y, guesses )
        fitX = numpy.linspace( xArray[min], xArray[max - 1], 100 )
        fitY = fit.function( fitX, *params )
        self.fit = ( ( fitX, fitY ) , params, fit, plot )
        self.plot()

    def removeFit( self ):
        self.fit = None
        self.plot()

    def setLength( self, length ):
        self._length = length
        self.lengthChanged.emit( length )

    length = property( lambda self: self._length, setLength )

    @property
    def yPlots( self ):
        return self.yPlotModel.yPlots

class Plot:
    def __init__( self, array, axis, color ):
        self.array = array
        self.axis = axis
        self.color = color

class YPlotModel( QtCore.QAbstractListModel ):
    def __init__( self, parent ):
        super( YPlotModel, self ).__init__( parent )
        self.yPlots = []

    def rowCount( self, parent = QtCore.QModelIndex() ):
        return len( self.yPlots )

    def data( self, index, role ):
        if not index.isValid():
            return QtCore.QVariant()
        yPlot = self.yPlots[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return yPlot.axis.name
        if role == QtCore.Qt.DecorationRole:
            return QtGui.QColor( yPlot.color )

    def addYPlot( self, array, axis ):
        self.beginInsertRows( QtCore.QModelIndex(), len( self.yPlots ), len( self.yPlots ) )
        self.yPlots.append( Plot( array, axis, colors[len( self.yPlots ) % len( colors )] ) )
        self.endInsertRows()

    def clearYPlots( self ):
        if self.yPlots:
            self.beginRemoveRows( QtCore.QModelIndex(), 0, len( self.yPlots ) - 1 )
            for i in range( len( self.yPlots ) ):
                self.yPlots.pop()
            self.endRemoveRows()

