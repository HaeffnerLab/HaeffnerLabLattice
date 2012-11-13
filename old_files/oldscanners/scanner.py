'''
Created on Feb 1, 2011

@author: christopherreilly
'''

#===============================================================================
# 2011 - 02 - 02
# 
# Logical structure for scan client created.
# 
# An experiment is composed of certain fundamental units:
# 
#    Function - wrapper for a normal python function
#    Scan - possesses a scanStep that possesses a parameter that is scanned
#    Sequence - an ordered list of steps
#    Repeat - repeats a step a specified number of times
# 
# Scans, Sequences, and Repeats are allowed to possesses
# all four of the fundamental units.  A Function may only
# possess a callable python function.  Thus every chain will
# end in a function being called.
# 
# In order for the four units to interact, it it necessary
# that each unit possess certain methods.  These methods are:
# 
#    execute()
# 
#        Execute the unit.
# 
#    getUnsetPars()
# 
#        Retrieve any unset parameters.  Each unit returns
#        its own dictionary - like object, which can be
#        unraveled using printUnsetPars()
# 
#    setPars()
# 
#        Set any of the unset parameters by passing in a
#        tuples as arguments.
# 
# It could be said then that each unit implements a unified
# interface ( we could call it the 'Action' interface ).
# 
# Many of the parameters of the unit can be made settable
# by assigning an Input object to the parameter.
# getUnsetPars() then indicates which of these parameters
# possess Input objects are their value.
# 
# TODO: Use zope interface system.
# TODO: Make non-scan parameters resettable.
# TODO: Organize all data, not just settables.
#===============================================================================

#===============================================================================
# 2011 - 02 - 02
# 
# There remains some issues with using units twice.
# It should be discussed the desired behavior in this situation.
#===============================================================================

#===============================================================================
# 2011 - 02 - 03
# 
# Cleaned up Function parameter setting.
# Scans now revert to their original, pre -
# execution state after execution.
# 
# Added argument list option to Function.
# 
# An alternative to using an argument list,
# which is required for labRAD settings, is
# to create a wrapper to your desired labRAD
# setting.
#===============================================================================

#===============================================================================
# 2011 - 02 - 03
# 
# Should everything take an input as a parameter?
#===============================================================================

class ScannerError( Exception ):
    errorDict = {
        0: 'Unset parameters remain',
        1: 'Scan parameter improperly configured',
        2: 'Attempted to set scan parameter before setting scan step',
        3: 'Attempted to execute Function with parameter marked for scanning',
        4: 'Input ID must be non-negative integer'
        }
    def __init__( self, code ):
        self.code = code
    def __repr__( self ):
        return '%d: %s' % ( self.code, self.errorDict[self.code] )

def printUnsetPars( dict, indent = 0 ):
    """
    Recieves a unit Dict object and prints in readable form.
    
    @param dict: unit Dict object (acquired through getUnsetPars())
    @param indent: parameter used recursively for indentation (don't assign)
    
    @return: None (prints to console)
    """
    def appInd( toPrint, indent ):
        """
        Prints with desired indentation.  Don't use.
        
        @param toPrint: String to be printed
        @param indent: amount of indentation (int)
        
        @return: None. prints to console
        """
        print '%s%s\n' % ( ''.join( '  ' for i in range( indent ) ), toPrint )
    #Handle for each type of Dict
    if isinstance( dict, Function.Dict ):
        appInd( 'Function:', indent )
        appInd( 'Unset parameters:', indent + 1 )
        if not dict.unset: appInd( 'None', indent + 2 )
        else:
            for key, value in dict.unset.items():
                appInd( '%s: %s' % ( key, value ), indent + 2 )
    elif isinstance( dict, Scan.Dict ):
        appInd( 'Scan:', indent )
        appInd( 'Unset scan params:', indent + 1 )
        if dict.unset:
            for key, value in dict.unset.items():
                appInd( '%s: %s' % ( key, value ), indent + 2 )
        else: appInd( 'None', indent + 2 )
        appInd( 'Unset step params:', indent + 1 )
        #See here how the indentation and Dicts are passed recursively
        printUnsetPars( dict.scanStep, indent + 2 ) if dict.scanStep else appInd( 'scan step unset' , indent + 2 )
    elif isinstance( dict, Sequence.Dict ):
        appInd( 'Sequence:', indent )
        for i, step in enumerate( dict.paramsByStep ):
            appInd( 'Step %d:' % ( i + 1 ), indent + 1 )
            printUnsetPars( step, indent + 2 )
    elif isinstance( dict, Repeat.Dict ):
        appInd( 'Repeat:', indent )
        appInd( 'To Repeat:', indent + 1 )
        printUnsetPars( dict.unset, indent + 2 )

class Input:
    """
    Object assigned to a parameter to indicate 
    that parameter is to be set later.
    
    Inputs can be assigned to any parameter when 
    instantiating any Function, Scan, or unit.
    TODO: Allow Inputs for Repeat unit.
    
    @param ID: Inputs with the same are logically identical.
    @param datatype: Indicates what datatype should be assigned
    @param desc: Short description of what the parameter does
    TODO: More robust identification scheme
    TODO: Should every parameter be an input?
    """
    def __init__( self, ID, datatype, desc ):
        if not isinstance( ID, int ) or ID < 0: raise ScannerError( 4 )
        self.datatype = datatype
        self.desc = desc
        self.ID = ID
    def __repr__( self ):
        return 'ID #' + str( self.ID ) + ' - ' + ( self.desc if self.desc else 'No description' )

class Function:
    """
    Possesses a function that will execute 
    with the specified parameters when we call
    the action's execute() method.
    
    @param func: Function to execute
    @param params: dict of function parameters
    """
    class Dict:
        def __init__( self, function, unset ):
            self.function = function
            self.unset = unset

    def __init__( self, function, *params, **kwparams ):
        self._func = function
        self._unset = {}
        for key, value in kwparams.items():
            if isinstance( value, Input ):
                self._unset[key] = kwparams.pop( key )
        self._set = kwparams
        for index, param in enumerate( params ):
            if isinstance( param, Input ):
                input = param
                self._unset[index] = input
            else: self._set[index] = param
        self._scan = {}

    def getUnsetPars( self ):
        function = self._func.__name__
        unset = self._unset
        return self.Dict( function, unset )

    def setPars( self, *toSet ):
        for ID, value in toSet:
            if ID == 'SCAN':
                for param, input in self._unset.items():
                    if value == input.ID:
                        self._scan[param] = ( None, self._unset.pop( param ) )
            elif ID == 'RESET':
                for param, tup in self._scan.items():
                    tmp, input = tup
                    if value == input.ID:
                        self._scan[param] = ( None, input )
            else:
                for param, tup in self._scan.items():
                    tmp, input = tup
                    if ID == input.ID:
                        self._scan[param] = ( value, input )
                for key, input in self._unset.items():
                    if ID == input.ID:
                        self._set[key] = value
                        del self._unset[key]

    def execute( self ):
        if self._unset: raise ScannerError( 0 )
        for param, scanValue in self._scan.items():
            value, input = scanValue
            if value is None: raise ScannerError( 3 )
            self._set[param] = value
        args = []
        kwargs = {}
        for key in sorted( self._set ):
            if isinstance( key, int ): args.append( self._set[key] )
            else: kwargs[key] = self._set[key]
        self._func( *args, **kwargs )
        for param in self._scan: del self._set[param]

class Scan:
    """
    Executes a unit multiple times, scanning one of the
    unit's parameters.
    
    @param scanStep: Unit to execute for each step
    @param min: Minimum scan value
    @param max: Maximum scan value
    @param steps: Number of steps in scan (linear interpolation)
    
    Once the scan object is initialized, it's scan parameter can 
    be set using the setScanPar() method.
    
    TODO: Allow for int values of min and max
    """
    class Dict:
        def __init__( self, scanStep, unset ):
            self.scanStep = scanStep
            self.unset = unset

    def __init__( self, scanStep, min, max, steps ):
        def checker( input ):
            for param, key in input:
                if isinstance( param, Input ):
                    unset[key] = param
                else: set[key] = param
        set = {}
        unset = {}
        checker( zip( ( scanStep, min, max, steps ),
                      ( 'scanStep', 'min', 'max', 'steps' ) ) )
        self._set = set
        self._unset = unset
        self._scanID = None

    def getUnsetPars( self ):
        scanStep = self._set.get( 'scanStep', None )
        if scanStep: scanStep = scanStep.getUnsetPars()
        unset = self._unset
        return self.Dict( scanStep, unset )

    def setScanPar( self, scanID ):
        scanStep = self._set.get( 'scanStep', None )
        if scanStep is None: raise ScannerError( 2 )
        scanStep.setPars( ( 'SCAN', scanID ) )
        self._scanID = scanID

    def setPars( self, *toSet ):
        for ID, value in toSet:
            for param, input in self._unset.items():
                if ID == input.ID:
                    self._set[param] = value
                    del self._unset[param]
        if self._scanID is not None:
            for ID, value in toSet:
                if ID == self._scanID:
                    print 'Blocking attempt to illegally assign scan parameter'
                    toSet = list( toSet )
                    toSet.remove( ( ID, value ) )
        scanStep = self._set.get( 'scanStep', None )
        if scanStep: scanStep.setPars( *toSet )

    def execute( self ):
        if self._unset or self._scanID is None: raise ScannerError( 0 )
        params = self._set
        min, max, steps, scanStep, scanID = ( params['min'],
                                              params['max'],
                                              params['steps'],
                                              params['scanStep'],
                                              self._scanID )
        for i in range( steps ):
            value = ( max - min ) * float( i ) / ( steps - 1 ) + min
            scanStep.setPars( ( scanID, value ) )
            scanStep.execute()
        scanStep.setPars( ( 'RESET', scanID ) )

class Sequence:
    """
    Executes an ordered list of units
    
    @param list: Initial sequence.
    
    This list can be augmented using the
    addStep() method.
    """
    class Dict:
        def __init__( self, paramsByStep ):
            self.paramsByStep = paramsByStep

    def __init__( self, *steps ):
        self.seq = []
        self.seq.extend( steps )

    def addStep( self, step, index = None ):
        if index is not None: self.seq.insert( index, step )
        else: self.seq.append( step )

    def setPars( self, *toSet ):
        for step in self.seq:
            step.setPars( *toSet )

    def getUnsetPars( self ):
        d = [step.getUnsetPars() for step in self.seq]
        return self.Dict( d )

    def execute( self ):
        for step in self.seq:
            step.execute()

class Repeat:
    """
    Repeats a unit a specified number of times.
    
    @param repAction: unit to repeat
    @param repeats: number of times to repeat unit
    """
    class Dict:
        def __init__( self, unset ):
            self.unset = unset
    def __init__( self, repAction, repeats ):
        self._action = repAction
        self._repeats = repeats
    def getUnsetPars( self ):
        unset = self._action.getUnsetPars()
        return self.Dict( unset )
    def setPars( self, *toSet ):
        self._action.setPars( *toSet )
    def execute( self ):
        for i in range( self._repeats ):
            self._action.execute()
