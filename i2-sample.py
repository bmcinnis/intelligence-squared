import re, numpy

filepath = r'~\debateData.txt'
with open(filepath, 'rb') as f:
    debateData = f.readlines()

delim = "#*|*#"
dD = [d.strip("\n").split(delim)  for d in debateData]
dD_vars = dD[0]
dD = numpy.array(dD[1:])


filepath = r'~\debateResults.txt'
with open(filepath, 'rb') as f:
    debateResults = f.readlines()

delim = "#*|*#"
dR = [d.strip("\n").split(delim)  for d in debateResults]
dR_vars = dR[0]
dR = numpy.array(dR[1:])
