'''
Created on Feb 3, 2011

@author: christopherreilly
'''
from __future__ import with_statement

def isUnit( unit ):
    """
    Naive way of ensuring that the unit we
    are about to assign implements the unit
    interface.
    """
    try:
        for attribute in ( 'execute', 'getInfo' ):
            if not hasattr( unit.__getattribute__( attribute ),
                            '__call__' ):
                raise ScannerError( '%s does not implement unit methods' % repr( unit ) )
    except AttributeError:
        raise ScannerError( '%s does not implement unit methods' % repr( unit ) )

def checkType( obj, *cls ):
    """
    Takes an object and sees if it is an instance 
    any of the following classes.
    """
    if 'function' in cls:
        cls = list( cls ).remove( 'function' )
        if cls:
            cls = tuple( cls )
            if not hasattr( obj, '__call__' ) or not isinstance( obj, cls ):
                raise ScannerError( '%s is not of type %s and is not callable' % ( repr( obj ), ' or '.join( [i.__name__ for i in cls] ) ) )
        else:
            if not hasattr( obj, '__call__' ):
                raise ScannerError( '%s is not callable' % repr( obj ) )
    else:
        if not isinstance( obj, cls ):
            raise ScannerError( '%s is not of type %s' % ( repr( obj ), ' or '.join( [i.__name__ for i in cls] ) ) )

class ScannerError( Exception ):
    pass

class Input( object ):
    """
    Every Parameter possesses an Input.
    
    Inputs contain three exposed properties:
    
        value - used on execution
        default - in case value is never set
        ID - used to identify Input instances
        description - should be short
        validator - ensure only valid values are set
        
    value and default can be assigned Link instances,
    which maps another Input's value using an 
    assigned mapping function.
    
    validators (optional) receive the value to be set as 
    input and should raise an exception if the value is 
    not valid.  Do not use lambdas as they can not be pickled.
    Consider using checkType in your own validator definition.
    Remember that you may want to allow Links as values.
    """
    def __init__( self, default, description = 'No description', validator = None ):
        if validator:
            checkType( validator, 'function' )
            self._validator = validator
            validator( default )
        self._default = default
        checkType( description, str )
        self._description = description

    def getValue( self ):
        if hasattr( self, '_value' ):
            return self._value
        return self.default

    def getDefault( self ):
        return self._default

    def getDescription( self ):
        return self._description

    def setDefault( self, default ):
        if hasattr( self, '_validator' ): self._validator( default )
        self._default = default

    def setDescription( self, description ):
        checkType( description, str )
        self._description = description

    def setValue( self, value ):
        if hasattr( self, '_validator' ): self._validator( value )
        self._value = value

    def delValue( self ):
        if hasattr( self, '_value' ):
            del self._value

    def getInfo( self ):
        if not hasattr( self, '_value' ): value = None
        else: value = self.value
        return self.Dict( self.description, self.default, value )

    class Dict:
        def __init__( self, description, default, value ):
            self.description = description
            self.default = default
            self.value = value

    default = property( getDefault, setDefault, None, None )
    description = property( getDescription, setDescription, None, None )
    value = property( getValue, setValue, delValue, None )

class Link( Input ):

    def __init__( self, input, map, *pars, **kwpars ):
        checkType( input, Input )
        self._input = input
        checkType( map, 'function' )
        self._map = map
        self._pars = pars
        self._kwpars = kwpars

    def getDefault( self ):
        return self.map( self.input.default, *self._pars, **self._kwpars )

    def setDefault( self ):
        raise ScannerError( 'Link instance can not set a default value' )

    def getDescription( self ):
        return 'Mapping of input with description: %s' % self.input.description

    def setDescription( self ):
        raise ScannerError( 'Link instance can not set description' )

    def setMap( self, map, *pars, **kwpars ):
        checkType( map, 'function' )
        self._map = map
        self._pars = pars
        self._kwpars = kwpars

    def getValue( self ):
        return self.map( self.input.value, *self._pars, **self._kwpars )

    def getInput( self ):
        return self._input

    def getMap( self ):
        return self._map

    def setInput( self, input ):
        checkType( input, Input )
        self._input = input

    def getInfo( self ):
        return self.Dict( self.input, self.map, self.pars, self.kwpars )

    input = property( getInput, setInput, None, None )
    map = property( getMap, setMap, None, None )
    default = property( getDefault, None, None, None )
    description = property( getDescription, None, None, None )
    value = property( getValue, None, None, None )

    class Dict:

        def __init__( self, input, map, pars, kwpars ):
            self.input = input
            self.map = {'Name':map.__name__, 'Doc':( map.__doc__.strip()
                                                               if map.__doc__
                                                               else 'No documentation' ) }
            self.pars = pars
            self.kwpars = kwpars

class Parameter( object ):
    """
    Parameter instances serve as a way 
    for a variable to interface with the 
    scanner framework.
    
    They possess a name, Input instance, and 
    and optional description.
    """
    def __init__( self, name, input = None, description = 'No description' ):
        checkType( name, str, int )
        self._name = name
        if input is not None: checkType( input, Input )
        self._input = input
        checkType( description, str )
        self._description = description

    def getName( self ):
        return self._name

    def getInput( self ):
        return self._input

    def getDescription( self ):
        return self._description

    def setInput( self, input ):
        checkType( input, Input )
        self._input = input

    def setDescription( self, description ):
        checkType( description, str )
        self._description = description

    def getInfo( self ):
        return self.Dict( self.name, self.description, self.input )

    class Dict:
        def __init__( self, name, description, input ):
            self.name = name
            self.description = description
            self.input = input

    name = property( getName, None, None, None )
    input = property( getInput, setInput, None, None )
    description = property( getDescription, setDescription, None, None )

class Action( object ):

    def __init__( self, function, *inputs, **kwinputs ):
        parameters = []
        for index, input in enumerate( inputs ):
            if input is not None: checkType( input, Input )
            parameters.append( Parameter( index, input ) )
        for name, input in kwinputs.items():
            if input is not None: checkType( input, Input )
            parameters.append( Parameter( name, input ) )
        checkType( function, 'function' )
        self._function = function
        self._parameters = parameters

    def getFunction( self ):
        return self._function

    def getParameters( self ):
        return self._parameters

    def getInfo( self ):
        return self.Dict( self.function, self.parameters )

    def execute( self ):
        tmp = {}
        for parameter in self.parameters:
            if parameter.input is None: raise ScannerError( "Action's parameter's input can not be None when executing" )
            tmp[parameter.name] = parameter.input.value
        args = []
        kwargs = {}
        for key in sorted( tmp ):
            if isinstance( key, int ):
                args.append( tmp[key] )
            else:
                kwargs[key] = tmp[key]
        self.function( *args, **kwargs )

    class Dict:

        def __init__( self, function, parameters ):
            self.function = {'Name':function.__name__, 'Doc':( function.__doc__.strip()
                                                               if function.__doc__
                                                               else 'No documentation' ) }
            self.parameters = parameters

    function = property( getFunction, None, None, None )
    parameters = property( getParameters, None, None, None )

class Scan( object ):

    def __init__( self, scanUnit, min, max, steps ):
        isUnit( scanUnit )
        self._scanUnit = Parameter( 'scanUnit',
                                    Input( scanUnit,
                                           validator = isUnit ) )
        self._min = Parameter( 'min',
                               Input( min,
                                      validator = floatChecker ) )
        self._max = Parameter( 'max',
                               Input( max,
                                      validator = floatChecker ) )
        self._steps = Parameter( 'steps',
                                 Input( steps,
                                        validator = intChecker ) )

    def getInfo( self ):
        return self.Dict( self._scanUnit,
                          self._min,
                          self._max,
                          self._steps,
                          self.scanInput )

    def execute( self ):
        scanUnit, min, max, steps, input = ( self.scanUnit,
                                             self.min,
                                             self.max,
                                             self.steps,
                                             self.scanInput )
        for i in range( steps ):
            value = ( max - min ) * float( i ) / ( steps - 1 ) + min
            input.value = value
            scanUnit.execute()
        del input.value

    class Dict:
        def __init__( self, scanUnit, min, max, steps, input ):
            self.scanUnit = scanUnit
            self.min = min
            self.max = max
            self.steps = steps
            self.input = input

    #===========================================================================
    # Properties
    #===========================================================================
    def getScanUnit( self ):
        return self._scanUnit.input.value
    def getMin( self ):
        return self._min.input.value
    def getMax( self ):
        return self._max.input.value
    def getSteps( self ):
        return self._steps.input.value
    def setScanUnit( self, scanUnit ):
        self._scanUnit.input.value = scanUnit
    def setMin( self, min ):
        self._min.input.value = min
    def setMax( self, max ):
        self._max.input.value = max
    def setSteps( self, steps ):
        self._steps.input.value = steps
    def delMin( self ):
        del self._min.input.value
    def delMax( self ):
        del self._max.input.value
    def delSteps( self ):
        del self._steps.input.value
    def getScanInput( self ):
        if not hasattr( self, '_scanInput' ):
            return None
        else: return self._scanInput
    def setScanInput( self, input ):
        #input must be base class Input (not Link)
        if type( input ) is not Input:
            raise ScannerError( '%s must be of type Input' % repr( input ) )
        self._scanInput = input
    scanInput = property( getScanInput, setScanInput, None, None )
    scanUnit = property( getScanUnit, setScanUnit, None, None )
    min = property( getMin, setMin, delMin, None )
    max = property( getMax, setMax, delMax, None )
    steps = property( getSteps, setSteps, delSteps, None )

class Sequence( object ):

    def __init__( self, *units ):
        for unit in units: isUnit( unit )
        self._sequence = list( units )

    def getInfo( self ):
        return self.Dict( self.sequence )

    def addUnit( self, unit, index = None ):
        """
        Add unit to sequence at specified index.
        If no index specified, append sequence with unit.
        """
        isUnit( unit )

    def execute( self ):
        for unit in self.sequence:
            unit.execute()

    class Dict:

        def __init__( self, sequence ):
            self.sequence = sequence

    #===========================================================================
    # Properties
    #===========================================================================
    def getSequence( self ):
        return self._sequence
    sequence = property( getSequence, None, None, None )

class Repeat( object ):

    def __init__( self, repeatUnit, repeats ):
        isUnit( repeatUnit )
        self._repeatUnit = Parameter( 'repeatUnit',
                                    Input( repeatUnit,
                                           validator = isUnit ) )
        self._repeats = Parameter( 'repeats',
                               Input( repeats,
                                      validator = intChecker ) )

    def getInfo( self ):
        return self.Dict( self._repeatUnit, self._repeats )

    def execute( self ):
        for i in range( self.repeats ):
            self.repeatUnit.execute()

    class Dict:

        def __init__( self, repeatUnit, repeats ):
            self.repeatUnit = repeatUnit
            self.repeats = repeats

    #===========================================================================
    # Properties
    #===========================================================================
    def getRepeatUnit( self ):
        return self._repeatUnit.input.value
    def getRepeats( self ):
        return self._repeats.input.value
    def setRepeatUnit( self, repeatUnit ):
        self._repeatUnit.input.value = repeatUnit
    def setRepeats( self, repeats ):
        self._repeats.input.value = repeats
    def delRepeats( self ):
        del self._repeats.input.value
    repeatUnit = property( getRepeatUnit, setRepeatUnit, None, None )
    repeats = property( getRepeats, setRepeats, delRepeats, None )

def floatChecker( fl ):
    checkType( fl, float, Link )

def intChecker( i ):
    checkType( i, int, Link )



