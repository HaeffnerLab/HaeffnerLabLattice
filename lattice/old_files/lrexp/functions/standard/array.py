'''
Array operations.
'''
def index( collection, beginning, end = None ):
    """
    Gets a subset of a collection.  Gets a single index if end is None or not specified.
    """
    return collection[beginning] if end is None else collection[beginning:end]

def append( collection, toAppend ):
    from copy import copy as duplicate
    """
    Appends the second argument to a copy of the first and returns the appended list.
    This uses a shallow copy operation.
    """
    copy = duplicate( collection )
    copy.append( toAppend )
    return copy

def group( *arguments ):
    """
    Creates a list of the arguments
    """
    return list( arguments )
