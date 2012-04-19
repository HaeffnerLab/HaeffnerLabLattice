def program(pboxserver, varDict):
    """Programs Paul's box using the dictionary format"""
    sequence = varDict['sequence']
    del varDict['sequence']
    progArray = []
    for key in varDict:
        progArray.append(['FLOAT',key,str(varDict[key])])
    pboxserver.send_command(sequence,progArray)