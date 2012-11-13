'''
Created on Mar 18, 2011

@author: christopherreilly
'''
try:
    from lrexp.components import Action, Sequence, Map
    from lrexp.util import runExperiment

    def addOne( x ): return x + 1

    a = Action( 'my action', addOne )
    b = Action( 'add one', addOne )
    a.parameters[0].input.value = 3
    b.parameters[0].input = Map( addOne )
    b.parameters[0].input.parameters[0].input = a.result
    s = Sequence( 'my seq', a, b )

    runExperiment( s )
    print 'Test Successful!'
except:
    print 'Test Failed!'
    raise
