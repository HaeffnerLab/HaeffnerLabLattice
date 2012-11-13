'''
Created on Apr 20, 2011

@author: SAM FENDELL
'''
from PyQt4 import QtGui, QtCore

from sympy import sympify, Symbol, lambdify


class Fit:
    def __init__( self, name, description, function, params, autofit = None ):
        self.name = name
        self.description = description
        self.function = function
        self.params = params
        self.autofit = autofit

def resAutofit( x, y ):
    xR = x.max() - x.min()
    yR = y.max() - y.min()
    area = ( xR ) * ( yR ) / 2
    mean = ( xR ) / 2 + x.min()
    sd = xR / 4
    offset = y.min()
    return area, mean, sd, offset
def linAutofit( x, y ):
    slope = ( y.max() - y.min() ) / ( x.max() - x.min() )
    return slope, y.min() - slope * x.min()

def sinAutofit( x, y ):
    height = ( y.max() - y.min() ) / 2
    wl = x.max() - x.min()
    phase = 0
    offset = y.min() + height
    return wl, phase, height, offset

def parabAutofit( x, y ):
    yCenter = y[y.size / 2]
    mean = ( x.max() - x.min() ) / 2
    lc = ( y.max() - y.min() ) / ( x.max() - x.min() )**2
    offset = yCenter
    if yCenter > y[0]:
        lc = -1 * lc
    return mean, lc, offset




GAUSSIAN = Fit( "Gaussian", 'Normal distribution',
                lambda x, height, mean, sd, offset: offset + height / ( numpy.sqrt( 2.0 * numpy.pi * sd ) ) * numpy.exp( -1.0 * ( ( x - mean ) / ( numpy.sqrt( 2.0 ) * sd ) ) ** 2 ),
                ( "Area", "Mean", "Variance", "Offset" ), resAutofit )
LORENTZ = Fit( "Lorentzian", 'Lorentzian distribution',
               lambda x, height, mean, sd, offset: offset + height / ( 1 + ( ( x - mean ) / sd ) ** 2 ),
               ( "Area", "Mean", "Half Width Half Max", "Offset" ), resAutofit )
LINE = Fit ( "Linear", 'Linear Fit',
            lambda x, slope, yint : yint + slope * x,
            ( "Slope", "Y intercept" ) , linAutofit )
SINE = Fit( "Sine", 'Sinusoidal Fit',
           lambda x, wl, phase, height, os: os + height * numpy.sin( x * 2 * numpy.pi / wl + phase ),
           ( "Wavelength", "Phase", "Amplitude", "Offset" ), sinAutofit )
PARAB = Fit( "Parabolic", 'Parabolic Fit',
            lambda x, mean, slope, offset: offset + slope * ( x - mean ) ** 2,
            ( "Mean", "Leading Coefficient", "Offset" ), parabAutofit )
FITTUP = ( GAUSSIAN, LORENTZ, LINE, SINE, PARAB )
import numpy
class FitDialog( QtGui.QDialog ):
    def __init__( self, model, parent ):
        super( FitDialog, self ).__init__( parent )
        self.setLayout( QtGui.QVBoxLayout() )

        self.layout().addWidget( QtGui.QLabel( '<big><b>Fit Data</b></big>', self ) )

        self.layout().addWidget( QtGui.QLabel( '<b>Select plot</b>' ) )
        self.plotList = QtGui.QComboBox( self )
        self.plotList.setModel( model )
        self.layout().addWidget( self.plotList )

        self.layout().addWidget( QtGui.QLabel( '<b>Select fit</b>' ) )
        self.fitList = QtGui.QComboBox( self )
        self.fitList.setModel( FitsModel( self ) )
        for fit in FITTUP:
            self.fitList.model().addFit( fit )

        newCustomFit = QtGui.QPushButton( 'Custom Fit', self )
        newCustomFit.clicked.connect( self.customSelected )

        fitRow = QtGui.QWidget( self )
        fitRow.setLayout( QtGui.QHBoxLayout() )
        fitRow.layout().addWidget( self.fitList, 1 )
        fitRow.layout().addWidget( newCustomFit )
        self.layout().addWidget( fitRow )

        self.checkBox = QtGui.QCheckBox( "Autofit", self )
        self.checkBox.setChecked( True )
        self.fitList.currentIndexChanged.connect( lambda row: self.checkBox.setEnabled( bool( self.fitList.model().fits[row].autofit ) ) )
        self.layout().addWidget( self.checkBox, 0, QtCore.Qt.AlignLeft )

        resultButtons = QtGui.QWidget( self )
        resultButtons.setLayout( QtGui.QHBoxLayout() )
        fitButton = QtGui.QPushButton( 'Apply fit', self )
        fitButton.clicked.connect( self.accept )
        cancelButton = QtGui.QPushButton( 'Cancel', self )
        cancelButton.clicked.connect( self.reject )
        resultButtons.layout().addWidget( fitButton )
        resultButtons.layout().addWidget( cancelButton )
        self.layout().addWidget( resultButtons )



    def customSelected( self ):
        title = 'New custom fit'
        funcName, result = QtGui.QInputDialog.getText( self, title, 'Enter fit name' )
        if not result:
            return
        funcName = str( funcName )
        funcDesc, result = QtGui.QInputDialog.getText( self, title, 'Enter fit description' )
        if not result:
            return
        funcDesc = str( funcDesc )
        error = None
        while( True ):
            function, result = QtGui.QInputDialog.getText( self, title, 'Enter an expression with "x" as independent variable, using p_(name) format for parameters' if error is None else error )
            if not result:
                return
            try:
                function = sympify( str( function ) )
                symbols = filter( lambda atom: type( atom ) is Symbol, function.atoms() )
                if Symbol( 'x' ) not in symbols:
                    error = 'Expression must by a function of "x"'
                    continue
                symbols.insert( 0, symbols.pop( symbols.index( Symbol( 'x' ) ) ) )
                function = lambdify( symbols, function, numpy )
                function( *[1.0 for symbol in symbols] )
            except:
                error = 'Error sympifying/lambdifying'
                raise
                continue
            params = [repr( x ) for x in symbols]
            params.remove( "x" )
            if any( [p[:2] != 'p_' for p in params] ):
                error = 'Parameters must begin with "p_"'
                continue
            break
        params = [h[2:] for h in params]
        newFit = Fit( funcName, funcDesc, function, params )
        self.fitList.model().addFit( newFit )
        self.fitList.setCurrentIndex( self.fitList.model().fits.index( newFit ) )


class FitsModel( QtCore.QAbstractListModel ):
    def __init__( self, parent ):
        super( FitsModel, self ).__init__( parent )
        self.fits = []
    def rowCount( self, parent = QtCore.QModelIndex() ):
        return len( self.fits )
    def data( self, index, role ):
        if not index.isValid():
            return QtCore.QVariant()
        fit = self.fits[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return fit.name
        if role == QtCore.Qt.ToolTipRole:
            return '%s (%s)' % ( fit.description, ', '.join( fit.params ) )
    def addFit( self, fit ):
        self.beginInsertRows( QtCore.QModelIndex(), len( self.fits ), len( self.fits ) )
        self.fits.append( fit )
        self.endInsertRows()

