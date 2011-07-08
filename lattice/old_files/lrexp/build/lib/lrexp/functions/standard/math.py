'''
Mathematical operations
'''
def summation( *summands ):
    """
    Sums the arguments
    """
    return sum( summands )

def multiply( *factors ):
    """
    Multiplies the arguments together
    """
    return reduce( lambda x, y: x * y, factors )

def divXY( x, y ):
    """
    Divides the first argument by the second, returns the result
    """
    return x / y

def average( *terms ):
    """
    Averages the arguments
    """
    return sum( terms ) / float( len( terms ) )
