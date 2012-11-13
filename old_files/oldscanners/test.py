from scannerplus import Input, Link, Action, Scan, Sequence, Repeat, checkType

def printNum( n ):
    print n

def printLine():
    print '----------------------------'

def printStars():
    print '*-*-*-*-*'

print 'Beginning of test:'
printLine()

print 'Configuring action:'
inputA = Input( 99, 'A number that will be printed', lambda x: checkType( x, int, float ) )
action = Action( printNum, inputA )
action.parameters[0].description = 'The number to be printed'
actionPar = action.parameters[0]
print 'action parameter:\n\t%s - %s\n\tInput: %s - %s' % ( actionPar.name, actionPar.description, actionPar.input.description, actionPar.input.value )
printLine()

print 'Executing Action:'
action.execute()
printLine()

print 'Executing Scan:'
scanA = Scan( action, 30.0, 33.0, 4 )
scanA.scanInput = actionPar.input
scanA.execute()
printLine()

print 'Executing Scan of Scan:'
scanB = Scan( scanA, 4.0, 6.0, 3 )
scanB.scanInput = scanA.getInfo().min.input
scanA.getInfo().max.input = Link( scanB.scanInput, lambda x: x + 3.0 )
scanB.execute()
printLine()

print 'Executing first Scan again:'
scanA.execute()
printLine()

print 'Executing Sequence'
starAction = Action( printStars )
lineAction = Action( printLine )
sequence = Sequence( starAction,
                     Action( printNum, Input( 'Beginning of sequence.' ) ),
                     scanA,
                     starAction,
                     scanB,
                     starAction,
                     action,
                     Action( printNum, Input( 'End of sequence.' ) ),
                     starAction )
sequence.execute()
printLine()

print 'Executing Repeat'
repeat = Repeat( Sequence( Action( printNum, Input( 'Beginning of repeat:' ) ),
                           sequence ), repeats = 3 )
repeat.execute()
