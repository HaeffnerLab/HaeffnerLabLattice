'''
Created on Feb 10, 2011

@author: christopherreilly
'''
from __future__ import with_statement
import pickle

FUNCTION = -397866

def runExperiment( unit, steps = None , reset = True, callback = None, *args, **kwargs ):
    """
    Convenience function for running experiments.
    Will call next() on a unit steps times, with the result of the call being passed into the first argument of the callback, with the args and kwargs passed in from there.
    If no steps specified (or is None or some negative integer), unit runs until completion.
    If no callback specified, next() is just called without the result being passed anywhere else.
    Handles initialization of unfinished experiments.
    """
    def doNothing( c, *args, **kwargs ): pass
    if callback is None: callback = doNothing
    if steps is None: steps = -1
    i = 0
    done = False
    while i != steps:
        try:
            callback( unit.next(), *args, **kwargs )
            i += 1
        except LRExpSignal, signal:
            callback( signal.chain, *args, **kwargs )
            done = True
            break
    if not done and reset: unit.initialize()

def checkType( obj, *cls ):
    """
    Takes an object and sees if it is an instance 
    any of the following classes.
    """
    if FUNCTION in cls:
        cls = list( cls ).remove( FUNCTION )
        if cls:
            cls = tuple( cls )
            if not callable( obj ) or not isinstance( obj, cls ):
                raise LRExpError( '%s is not of type %s and is not callable' % ( repr( obj ), ' or '.join( [i.__name__ for i in cls] ) ) )
        else:
            if not callable( obj ):
                raise LRExpError( '%s is not callable' % repr( obj ) )
    else:
        if not isinstance( obj, cls ):
            raise LRExpError( '%s is not of type %s' % ( repr( obj ), ' or '.join( [i.__name__ for i in cls] ) ) )

def saveUnit( unit, filename ):
    """
    Saves unit as a pickle file with .lre extension.
    
    So don't put .lre at the end of filename argument.
    """
    unit.initialize()
    unit.generator = None
    filename += '.lre'
    with open( filename, 'w' ) as file:
        pickle.dump( unit, file )
    print 'Saved unit'

def loadUnit( filename ):
    """
    Loads an unit from a .lre file with name filename.
    
    Returns an instance of the unit.
    """
    filename += '.lre'
    with open( filename, 'r' ) as file:
        unit = pickle.load( file )
    return unit

class LRExpError( Exception ):
    """
    Custom Exception
    """
    pass

class LRExpSignal( Exception ):
    """
    Used to track execution state.
    """
    def __init__( self, chain ):
        self.chain = chain

    def __repr__( self ):
        return repr( self.chain )

def printInfo( comp, indent = 0 ):
    """
    Prints information about component-tree
    """
    from components import Function, Unit, Input, Map, Parameter, Action, Scan, Sequence, Repeat

    def appInd( toPrint, indent ):
        indentString = ' - '
        print '%s%s\n' % ( ''.join( indentString for i in range( indent ) ), toPrint )
    compType = type( comp )
    appInd( repr( comp ), indent )
    if issubclass( compType, Input ):
        appInd( 'ID: %d' % comp.id, indent + 1 )
    if issubclass( compType, Unit ) and not compType is Action:
        appInd( 'Mode: %d' % comp.mode, indent + 1 )
    if issubclass( compType, Function ):
        appInd( 'Function:', indent + 1 )
        if comp.function is None:
            appInd( 'Not assigned' , indent + 2 )
        else:
            appInd( 'Name: %s' % comp.function.__name__ , indent + 2 )
            appInd( 'Doc: %s' % ( comp.function.__name__ if comp.function.__doc__ else 'None' ), indent + 2 )
            if len( comp.parameters ) > 0:
                appInd( 'Parameters:', indent + 1 )
                for parameter in comp.parameters.values():
                    printInfo( parameter, indent + 2 )
            if comp.argListEnabled:
                argList = comp.argList if type( comp.argList ) is list else [comp.argList]
                if len( argList ) > 0:
                    appInd( 'List Arguments:', indent + 1 )
                    for arg in argList:
                        printInfo( arg, indent + 2 )
    if isinstance( comp, Parameter ):
        printInfo( comp.input, indent + 1 )
        return
    if isinstance( comp, Scan ):
        appInd( 'Scan Unit:', indent + 1 )
        printInfo( comp.scanUnit if comp.scanInput else 'Not Assigned', indent + 2 )
        appInd( 'Scan Input:', indent + 1 )
        printInfo( comp.scanInput if comp.scanInput else 'Not Assigned', indent + 2 )
        appInd( 'Min:', indent + 1 )
        printInfo( comp.min.input, indent + 2 )
        appInd( 'Max:', indent + 1 )
        printInfo( comp.max.input, indent + 2 )
        appInd( 'Steps:', indent + 1 )
        printInfo( comp.steps.input, indent + 2 )
        return
    if isinstance( comp, Sequence ):
        appInd( 'Sequence steps:', indent + 1 )
        for index, unit in enumerate( comp.sequence ):
            appInd( '%d:' % index, indent + 2 )
            printInfo( unit, indent + 3 )
        return
    if isinstance( comp, Repeat ):
        appInd( 'Number of repeats:', indent + 1 )
        printInfo( comp.repeats.input, indent + 2 )
        appInd( 'Repeat Unit:', indent + 1 )
        printInfo( comp.repeatUnit, indent + 2 )
        return

if __name__ == "__main__":
    pass

