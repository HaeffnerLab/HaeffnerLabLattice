def getDataDirectory(regserver):
    """Returns the location of the data vault save directory on disk"""
    import os
    nodename = os.environ.get('LABRADNODE', None)
    regserver.cd(['','Servers','Data Vault','Repository'])
    dir = regserver.get(nodename)
    return dir