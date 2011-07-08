'''
Created on Feb 24, 2011

@author: christopherreilly
'''
import inspect
from util import FUNCTION, checkType, LRExpError, LRExpSignal
from lr import LabradSetting

class Unit( object ):
    """
    Abstract class that demonstrates the unit interface 
    as well as some implements some methods common to all 
    units.  Defines the modes and the generator, caller, 
    and toCall attributes.
    
    The caller and toCall properties ensure proper execution of 
    the unit.  If a different call chain attempts to call the next 
    method of a unit, the unit will reset its generator.
    
    Calling a unit's next method will return chain representing 
    the state of execution.  When the unit's generator falls off 
    the edge, it raises a LRExpSignal with itself as the only member 
    of the chain and its state set to None (unless overloaded by subclass).
    """
    #Smallest step
    PROBE = 0
    #Unit by unit
    STEP = 1
    #All units
    ALL = 2
    mode = PROBE
    _name = None

    def __init__( self, name = None ):
        self._name = name
        if type( self ) is Unit: raise LRExpError( 'Do not instantiate the Unit class' )

    def next( self, caller = ( 'TOP', ) ):
#        Doesn't need to be overridden, but if 
#        you would like to perform any additional 
#        cleanup when the generator stops, you can 
#        override, calling the superclass method and 
#        catching the LRExpSignal message it raises.
#        If you do this make sure to reraise
        self.caller = caller
        try:
            return self.generator.next()
        except StopIteration:
            del self.generator
            if self.caller == ( 'TOP', ):
                self.initialize()
                raise LRExpSignal( [self.signal()] )
            else:
                raise LRExpSignal( [self.signal()] )

    @classmethod
    def signal( cls, state = None ):
        return ( cls, state )

    def set( self ):
        """
        Classes implementing the Unit interface 
        override this method and make sure it sets the 
        generator attribute with a fresh generator. Should 
        refer to the unit's mode of execution (PROBE, STEP, or ALL).
        """
        def generator():
            pass
        self.generator = generator()
        self.generator.next()

    def initialize( self ):
        """
        Override this, calling the superclass method and 
        deleting/resetting any other necessary values, as 
        well as the values of any Units in possession.
        
        Called whenever a top-level generator completes.
        """
        del self.caller
        del self.generator
        del self.toCall

    def checkConfiguration( self ):
        if not self.configured: raise LRExpError( 'Unit not configured for execution' )

    #===========================================================================
    # Properties
    #===========================================================================
    def getCaller( self ):
        return self._caller
    def getConfigured( self ):
        return False
    def getGenerator( self ):
        if not hasattr( self, '_generator' ):
            self.set()
        return self._generator
    def getName( self ):
        if self._name is None:
            return '%s (No name)' % type( self ).__name__
        return self._name
    def getToCall( self ):
        return self._toCall
    def setCaller( self, caller ):
        if not hasattr( self, '_caller' ) or caller != self.caller:
            self._caller = caller
            toCall = list( caller )
            toCall.append( self )
            toCall = tuple( toCall )
            self._toCall = toCall
            self.set()
    def setGenerator( self, generator ):
        self._generator = generator
    def setName( self, name ):
        self._name = name
    def setToCall( self, toCall ):
        self._toCall = toCall
    def delCaller( self ):
        if hasattr( self, '_caller' ):
            del self._caller
    def delGenerator( self ):
        if hasattr( self, '_generator' ):
            del self._generator
    def delToCall( self ):
        if hasattr( self, '_toCall' ):
            del self._toCall
    caller = property( getCaller, setCaller, delCaller, None )
    configured = property( lambda self: self.getConfigured() )
    generator = property( getGenerator, setGenerator, delGenerator, None )
    name = property( getName, setName, None, None )
    toCall = property( getToCall, setToCall, delToCall, None )

    def __repr__( self ):
        return self.name

def isUnit( unit ):
    return isinstance( unit, Unit )

def forceUnit( unit ):
    """
    Ensures that the unit we are about to assign implements the unit interface.
    """
    if isUnit( unit ): return
    raise LRExpError( '%s does not implement unit methods' % repr( unit ) )

class Function( object ):
    """
    Abstract class that encapsulates the action of a python function
    
    Automatic creation of parameters and enabling/disabling of list arguments
    """
    def __init__( self, function = None ):
        if function is not None: checkType( function, FUNCTION )
        self.function = function
        if type( self ) is Function: raise LRExpError( 'Do not instantiate Function class' )

    def getArgs( self ):
        tmp = {}
        for key, parameter in self.parameters.items():
            tmp[key] = parameter.input.value
        ints = [key for key in tmp if type( key ) is int]
        max = len( ints )
        if self.argListEnabled:
            argList = self.argList.value if isinstance( self.argList, Input ) else [input.value for input in self.argList]
            for index, value in enumerate( argList ):
                tmp[index + max] = value
        args = []
        kwargs = {}
        for key in sorted( tmp ):
            if isinstance( key, int ):
                args.append( tmp[key] )
            else:
                kwargs[key] = tmp[key]
        return ( args, kwargs )

    #===========================================================================
    # Properties
    #===========================================================================
    @property
    def argListEnabled( self ):
        if self.function is None: return False
        if type( self.function ) is LabradSetting: return False
        return not inspect.getargspec( self.function )[1] is None
    def getFunction( self ):
        return self._function
    def setFunction( self, function ):
        self._function = function
        self.argList = []
        self.parameters = {}
        if function is None: return
        checkType( function, FUNCTION )
        if type( function ) is LabradSetting:
            self.parameters = {}
            if function.parameters is None:
                return
            [self.parameters.update( {index:Parameter( index, Input( None ), parameter )} ) for index, parameter in enumerate( function.parameters )]
            return
        argNames, defs = ( inspect.getargspec( function )[i] for i in ( 0, 3 ) )
        defs = [] if defs is None else defs
        argVals = [None for i in range( len( argNames ) - len( defs ) )]
        argVals.extend( defs )
        parameters = {}
        for index, argTup in enumerate( zip( argNames, argVals ) ):
            parameters[index] = Parameter( index, Input( argTup[1] ), argTup[0] )
        self.parameters = parameters
    function = property( getFunction, setFunction, None, None )

class Input( object ):
    """
    Every Parameter possesses an Input (or a subclass).
    
    Inputs contain these properties:
    
        value - used on execution
        ID - used to identify Input instances
        description - should be short
        validator - ensure only valid values are set (deprecated?)
    """

    def __init__( self, value, description = 'No description', validator = None ):
        if validator:
            checkType( validator, FUNCTION )
            self._validator = validator
            validator( value )
        self._value = value
        self.description = description

    #===========================================================================
    # Properties
    #===========================================================================
    def getValue( self ):
        return self._value
    @property
    def id( self ):
        return id( self )
    def setValue( self, value ):
        if hasattr( self, '_validator' ): self._validator( value )
        self._value = value
    value = property( lambda self: self.getValue(), lambda self, value: self.setValue( value ), None, None )

    def __repr__( self ):
        def shortRepr( s ):
            max = 30
            s = repr( s )
            if len( s ) > max:
                return s[:max] + '...'
            return s
        return '%s -> %s' % ( self.__class__.__name__, shortRepr( self.value ) )

class Global( Input ):
    def __init__( self, name, value ):
        super( Global, self ).__init__( value )
        self.name = name

    def __repr__( self ):
        return '%s (Global) -> %s' % ( self.name, repr( self.value ) )

class Map( Input, Function ):
    """
    An Input that maps many inputs to a single value using a function
    """
    def __init__( self, map, description = 'No description' ):
        super( Input, self ).__init__( map )
        self.description = description

    #===========================================================================
    # Properties
    #===========================================================================
    def getValue( self ):
        args, kwargs = self.getArgs()
        return self.function( *args, **kwargs ) if self.function else 'No function assigned'
    def setValue( self ):
        raise LRExpError( 'Map instance can not set value' )

    def __repr__( self ):
        repr = 'Map'
        try:
            value = self.value
            return '%s: %s' % ( repr, repr( value ) )
        except:
            return repr

class Parameter( object ):
    """
    Parameter instances serve as a way for a variable to interface with the Unit framework.
    
    They possess a name, Input instance (or subclass), and an optional description.
    """
    def __init__( self, name, input = None, description = 'No description' ):
        checkType( name, str, int )
        self._name = name
        if input is not None: checkType( input, Input )
        self._input = input
        checkType( description, str )
        self._description = description

    #===========================================================================
    # Properties
    #===========================================================================
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
    name = property( getName, None, None, None )
    input = property( getInput, setInput, None, None )
    description = property( getDescription, setDescription, None, None )

    def __repr__( self ):
        def shortRepr( s ):
            max = 35
            s = s if isinstance( s, str ) else repr( s )
            if len( s ) > max:
                return s[:max] + '...'
            return s
        name = self.name if isinstance( self.name, str ) else repr( self.name )
        return ( '%s (%s)' % ( name, shortRepr( self.description ) ) ) if self.description else name

class Action( Unit, Function ):
    """
    A Unit that calls a function with specified arguments when the next() method is called.  Only operates in one mode.
    """
    class Result( Input ):
        def __init__( self, parentAction ):
            super( Action.Result, self ).__init__( None, 'Action result' )
            self.parentAction = parentAction
        def getValue( self ):
            return self._value
        def setValue( self ):
            raise LRExpError( 'Result instance can not set value (only accessed internally through generator)' )
        def __repr__( self ):
            return 'Result for %s: %s' % ( self.parentAction.name, super( Action.Result, self ).__repr__() )

    def __init__( self, name = None, function = None ):
        self.result = self.Result( self )
        super( Unit, self ).__init__( function )
        super( Action, self ).__init__( name )

    def next( self, caller = ( 'TOP', ) ):
        try:
            super( Action, self ).next( caller )
        except LRExpSignal:
            raise LRExpSignal( [self.signal( self.result.value )] )

    def set( self ):
        def generator():
            """
            Extracts values from parameters and passes them 
            into the function.
            """
            chain = None
            yield chain
            args, kwargs = self.getArgs()
            self.result._value = self.function( *args, **kwargs )
        self.generator = generator()
        self.generator.next()

    def getConfigured( self ):
        return bool( self.function )

    def initialize( self ):
        super( Action, self ).initialize()
        self.result._value = None

    #===========================================================================
    # Properties
    #===========================================================================


Result = Action.Result

class Scan( Unit ):
    """
    Performs a scan over a specified unit for a specified range of values (floats).
    
    A scan possesses a scanUnit and scanInput.  The scanInput is expected to be a reference to an Input instance that is contained inside of the scanUnit.
    
    When we execute a scanUnit, it will set the scanInput's value member for each value of the range ( n equally spaced steps between min and max where n is specified by the steps parameter ), and then execute the entire scanUnit.
    """
    MARKEDFORSCANNING = '*** Marked for scanning ***'
    def __init__( self, name = None, scanUnit = None, min = None, max = None, steps = None ):
        super( Scan, self ).__init__( name )
        if scanUnit is not None: forceUnit( scanUnit )
        self.scanUnit = scanUnit

        self.min, self.max, self.steps = ( Parameter( name, Input( value, '' ), '' ) for name, value in ( ( 'Minimum', min if min is None else float( min ) ),
                                                                                                             ( 'Maximum', max if max is None else float( max ) ),
                                                                                                             ( 'Steps', steps if steps is None else int( steps ) ) ) )

    def set( self ):
        def generator():
            def calculateValue( i ):
                    return ( max - min ) * float( i ) / ( steps - 1 ) + min
            self.checkConfiguration()
            mode = self.mode
            yield None
            scanUnit, min, max, steps, input = ( self.scanUnit, self.min.input.value, self.max.input.value, self.steps.input.value, self.scanInput )
            chain = None
            if mode is self.PROBE:
                for i in range( steps ):
                    value = calculateValue( i )
                    input.value = value
                    try:
                        while True:
                            chain = scanUnit.next( self.toCall )
                            chain.append( self.signal( i ) )
                            yield chain
                    except LRExpSignal, signal:
                        chain = signal.chain
                        chain.append( self.signal( i ) )
            elif mode is self.STEP:
                for i in range( steps ):
                    value = calculateValue( i )
                    input.value = value
                    try:
                        while True:
                            scanUnit.next( self.toCall )
                    except LRExpSignal, signal:
                        chain = signal.chain
                        chain.append( self.signal( i ) )
                        yield chain
            elif mode is self.ALL:
                # Maybe error here (TODO)
                yield
                for i in range( steps ):
                    value = calculateValue( i )
                    input.value = value
                    try:
                        while True:
                            scanUnit.next( self.toCall )
                    except LRExpSignal, signal:
                        pass
            self.scanInput.value = self._tmpValue
            del self._tmpValue
        if not hasattr( self, '_tmpValue' ):
            self._tmpValue = self.scanInput.value
        self.generator = generator()
        self.generator.next()
        self.scanUnit.set()

    def initialize( self ):
        super( Scan, self ).initialize()
        if self.scanInput:
            self.scanInput.value = self.__dict__.get( '_tmpValue' )
        if self.scanUnit:
            self.scanUnit.initialize()

    def getConfigured( self ):
        return ( not None in ( self.scanInput, self.scanUnit, self.min, self.max, self.steps ) ) and self.scanUnit.configured

    #===========================================================================
    # Properties (small change)
    #===========================================================================
    def getScanInput( self ):
        if not hasattr( self, '_scanInput' ):
            return None
        else: return self._scanInput
    def setScanInput( self, input ):
        if type( input ) is not Input:
            raise LRExpError( '%s must be of type Input' % repr( input ) )
        if self.scanInput is not None:
            self.scanInput.description = self.__dict__.get( '_tmpDescription' )
            self.scanInput.value = self.__dict__.get( '_tmpValue' )
        self._tmpDescription = input.description
        self._tmpValue = input.value
        self._scanInput = input
        self.scanInput.description = self.MARKEDFORSCANNING
    scanInput = property( getScanInput, setScanInput, None, None )

class Sequence( Unit ):
    """
    Executes an ordered sequence of units.
    """

    def __init__( self, name = None, *units ):
        super( Sequence, self ).__init__( name )
        for unit in units: forceUnit( unit )
        self._sequence = list( units )

    def set( self ):
        def generator():
            chain = None
            mode = self.mode
            if mode is self.PROBE:
                for index, step in enumerate( self.sequence ):
                    try:
                        while True:
                            yield chain
                            chain = step.next( self.toCall )
                            chain.append( self.signal( index ) )
                    except LRExpSignal, signal:
                        chain = signal.chain
                        chain.append( self.signal( index ) )
                yield chain
            elif mode is self.STEP:
                for index, step in enumerate( self.sequence ):
                    yield chain
                    try:
                        while True:
                            step.next( self.toCall )
                    except LRExpSignal, signal:
                        chain = signal.chain
                        chain.append( self.signal( index ) )
            elif mode is self.ALL:
                yield chain
                for step in self.sequence:
                    try:
                        while True:
                            step.next( self.toCall )
                    except LRExpSignal, signal:
                        pass
        for unit in self.sequence: unit.set()
        self.generator = generator()
        self.generator.next()

    def initialize( self ):
        super( Sequence, self ).initialize()
        for step in self.sequence:
            step.initialize()

    def getConfigured( self ):
        return bool( self.sequence ) and not False in [unit.configured for unit in self.sequence]

    def addUnit( self, unit, index = None ):
        """
        Add unit to sequence at specified index.
        If no index specified, append sequence with unit.
        """
        forceUnit( unit )
        if index is None: self.sequence.append( unit )
        else: self.sequence.insert( index, unit )

    #===========================================================================
    # Properties
    #===========================================================================
    def getSequence( self ):
        return self._sequence
    sequence = property( getSequence, None, None, None )

class Repeat( Unit ):
    """
    Executes a unit a specified number of times.
    """

    def __init__( self, name = None, repeatUnit = None, repeats = 1 ):
        super( Repeat, self ).__init__( name )
        if repeatUnit is not None: forceUnit( repeatUnit )
        self.repeatUnit = repeatUnit
        self.repeats = Parameter( 'Repeats',
                               Input( repeats ) )
    def set( self ):
        def generator():
            mode = self.mode
            chain = None
            if mode is self.PROBE:
                for i in range( self.repeats.input.value ):
                    try:
                        while True:
                            yield chain
                            chain = self.repeatUnit.next( self.toCall )
                            chain.append( self.signal( i ) )
                    except LRExpSignal, signal:
                        chain = signal.chain
                        chain.append( self.signal( i ) )
            elif mode is self.STEP:
                for i in range( self.repeats.input.value ):
                    try:
                        yield chain
                        while True:
                            self.repeatUnit.next( self.toCall )
                    except LRExpSignal, signal:
                        chain = signal.chain
                        chain.append( self.signal( i ) )
            elif mode is self.ALL:
                yield
                for i in range( self.repeats.input.value ):
                    try:
                        while True:
                            self.repeatUnit.next( self.toCall )
                    except LRExpSignal, signal:
                        pass
        self.repeatUnit.set()
        self.generator = generator()
        self.generator.next()
    def initialize( self ):
        super( Repeat, self ).initialize()
        self.repeatUnit.initialize()
    def getConfigured( self ):
        return None not in ( self.repeats, self.repeatUnit ) and self.repeatUnit.configured


if __name__ == "__main__":
    pass
