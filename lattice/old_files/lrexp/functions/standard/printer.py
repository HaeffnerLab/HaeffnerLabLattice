'''
Printing to console
'''
def printX( toPrint ):
    """
    Takes in a value and prints it to console.
    """
    print toPrint

def printSpacer():
    """
    Marks a separation
    """
    print '-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*'

def printAll( *toPrint ):
    """
    Prints every argument
    """
    for x in toPrint: print x
