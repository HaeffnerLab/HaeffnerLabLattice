def getDataDirectory(regserver):
    """Returns the location of the data vault save directory on disk"""
    import os
    nodename = os.environ.get('LABRADNODE', 'localhost')
    regserver.cd(['','Servers','Data Vault','Repository'])
    directory = regserver.get(nodename)
    return directory