import re, numpy

filepath = r'/Users/bjm277/code/intelligence-squared/debateData.txt'
with open(filepath, 'rb') as f:
    debateData = f.readlines()

delim = "#*|*#"
dD = [d.strip("\n").split(delim)  for d in debateData]
dD_vars = dD[0]
dD = numpy.array(dD[1:])

debateData = [d.replace(delim,"|") for d in debateData]
f = open(filepath, 'wb')
f.writelines(debateData);
f.close

filepath = r'/Users/bjm277/code/intelligence-squared/debateResults.txt'
with open(filepath, 'rb') as f:
    debateResults = f.readlines()

delim = "#*|*#"
dR = [d.strip("\n").split(delim)  for d in debateResults]
dR_vars = dR[0]
dR = numpy.array(dR[1:])

debateResults = [d.replace(delim,"|") for d in debateResults]
f = open(filepath, 'wb')
f.writelines(debateResults);
f.close

print '--end--'
