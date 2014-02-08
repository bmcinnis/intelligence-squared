## Intelligence Squared US (I2US) - Getting Started
## Brian McInnis, Cornell University 2014

import imp

mods = ['os','pprint','pickle','re']
error = []
for m in mods:        
    try:
        imp.find_module(m)
    except:
        error.append(m)

if (len(error)>0):
    print """
---Please Install the following modules:
%s

*   I highly recommend installing the Python 'setuptools'
*       GO TO: (https://pypi.python.org/pypi/setuptools)
*   and then installing each module from the command line:
*       pip install <module>

""" %(",".join(error))
else:
    import os, pprint, pickle, re

    debateDir = 'i2Debates'
    debateFilePattern = '.*[.]p$'

    ## openDebate() Function that verifies the file is a file
    ##  and contains the appropriate filepath pattern (see debateFilePattern).
    ##  Successful filepath returns a python object from the pickle file
    def openDebate(filepath):
        if ((os.path.isfile(filepath))&(re.match(debateFilePattern,filepath)!=None)):
            debate = pickle.load(open( filepath,"rb"))
            return debate
        else:
            return False


    ## For display purposes, push the object to a graph/chart for inspection
    def pushToHTML(obj):
        return obj

    ## Offer edits to the Pickle data so that you can contribute to the GITHUB repository
    def pushToPickle(filepath,obj):
        ### Please don't screw around with the data, be mindful that this is an academic
        ###   effort, don't make me deal with junk or any malicious energy.  I really
        ###   do want meaningful collaboration.  There are cleaning errors, and there
        ###   are cool things we can do together through the project.  Thank you, Brian.
        if ((os.path.isfile(filepath))&(re.match(debateFilePattern,filepath)!=None)):
            pickle.dump(obj,open(filepath,"wb"))
            return True
        else:
            return False

    def speakerTurnFrequencies(debate):
    ## Return the unique set of SPEAKERS

        ### In case additional spaces were included in separating the speaker names
        ###   from the audience polling data before and after the debate. 
        for i in ['for','against','moderator']:
            debate[i] = [d.strip() for d in debate[i]]
    
        ### Create a list of all speaker tags from the text.  This is not a unique
        ###   so that we can get the frequency of turns per speaker.
        speakers = [d['SPEAKER'] for d in debate['text']]    

        ### Create an "Other" category based on the set difference
        debate['other'] = set(speakers).difference(set(debate['against']+debate['for']+debate['moderator']))

        ### Create the speakerTurns object as the frequency of each speaker
        ###   by their turns in the debate.
        speakerTurns = {
                        'for':dict([(t.strip(),speakers.count(t.strip())) for t in debate['for']]),
                        'against':dict([(t.strip(),speakers.count(t.strip())) for t in debate['against']]),
                        'moderator':dict([(t.strip(),speakers.count(t.strip())) for t in debate['moderator']]),
                        'other':dict([(t.strip(),speakers.count(t.strip())) for t in debate['other']])
                        }        
        return speakerTurns


###### Using the functions to access the data after having loaded
    ##   all of the appropriate modules, etc.
    
    ## Identify all of the pickle files associated with I2US debates
    debateFiles = ["%s/%s" %(debateDir,f) for f in os.listdir(debateDir+"/") if re.match(debateFilePattern,f)]

    ## Load a debate from its pickle file and return the turn taking frequency
    ##   by role and participant
    for d in debateFiles:
        debate = openDebate(filepath=d)
        speakerTurns = speakerTurnFrequencies(debate)
        print (d)
        pprint.pprint(speakerTurns)
