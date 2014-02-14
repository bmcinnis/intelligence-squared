## Intelligence Squared US (I2US) - Getting Started
## Brian McInnis, Cornell University (c) 2014
##      OBJECTIVE:  Present a few methods for accessing
##      the I2US pickle files and performing some
##      preliminary analysis of the aggregate data.
##
##      Use the python help() command to return descriptions
##      of the functions in this file [i.e., help(openDebate) ]

"""
    i2-getstarted.py:  A series of functions designed to
    support new users of the I2US data.
"""

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

    def openDebate(filepath):
        """
            openDebate(filepath):  Function that verifies the file is a file
            and contains the appropriate filepath pattern (see debateFilePattern).
            Successful filepath returns a python object from the pickle file
        """

        if ((os.path.isfile(filepath))&(re.match(debateFilePattern,filepath)!=None)):
            debate = pickle.load(open( filepath,"rb"))
            return debate
        else:
            return False

    def pushToPickle(filepath,obj):
        """
            pushToPickle(filepath, obj):  Function that takes a data object and
            string reference to a file path.  Compresses the object to a pickle
            file and reports True or False after attempting the compression.
        """
        if ((os.path.isfile(filepath))&(re.match(debateFilePattern,filepath)!=None)):
            pickle.dump(obj,open(filepath,"wb"))
            return True
        else:
            return False

    def correctDebates(correction,obj):
        """
            correctDebates():   Feed specific instructions to adjust the debate file
            in various ways.  This function is designed to be somewhat passive.
        """
        for c in correction.keys():
            if (c == "title"):
                obj[c] = correction[c]
            elif (c == "roles"):
                for r in correction[c].keys():
                    if (r in obj):
                        obj[r].extend(correction[c][r])
                        obj[r] = list(set(obj[r]))
                    else:
                        obj[r] = correction[c][r]
            elif (c == "speakers"):
                for l in obj['text']:
                    if l['SPEAKER'] in correction[c]:
                        l['SPEAKER'] = correction[c][l['SPEAKER']]
            elif (c == "sections"):
                obj[c] = {}
                catchAll = []
                fCurrentSection = ""
                for l in obj['text']:
                    fGoForth = True
                    tLine = l
                    if "TIME" in l:
                        fTime = [t for t in l["TIME"].keys() if t in correction[c]]
                        for f in fTime:
                            fBreak = l["TIME"][f]
                            fTitle = correction[c][f]
                            print "%s----%s: %s (%s)" %(c, f, fTitle, fBreak)
                            if (fCurrentSection !=""):
                                ## Remove the statements from prior section                                
                                tLine = tLine['STATEMENT'][0:fBreak-1]
                                if(len(tLine)>0):
                                    obj[c][fCurrentSection].append({'STATEMENT':tLine,
                                                                    'SPEAKER':l['SPEAKER']})
                            fCurrentSection = fTitle
                            obj[c].setdefault(fCurrentSection,[])
                            if(len(catchAll)>0):
                                obj[c][fCurrentSection].extend(catchAll)
                                catchAll = []
                            obj[c][fCurrentSection].append({'STATEMENT':l['STATEMENT'][fBreak-1:],
                                                            'SPEAKER':l['SPEAKER']})
                            fGoForth = False
                    if ((fGoForth == True)&(fCurrentSection !="")):
                        obj[c][fCurrentSection].append({'STATEMENT':l['STATEMENT'],
                                                'SPEAKER':l['SPEAKER']})
                    elif ((fGoForth == True)&(fCurrentSection == "")):
                        catchAll.append({'STATEMENT':l['STATEMENT'],
                                                'SPEAKER':l['SPEAKER']})
        return obj

    def speakerTurnFrequencies(debate):
        """
            speakerTurnFrequencies(debate):  Return the unique set of SPEAKERS

            This function provides some simple cleaning of the name values.
            In case additional spaces were included in separating the speaker names
            from the audience polling data before and after the debate.

            A unique list of the speakers is created, this is used to return
            the frequency of speaking turns, by speaker and by category (for, against,
            moderator, other).

            Return value is a nested dictionary of by category by name frequencies.
        """

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

    def splitWords(text):
        """
            Simply takes a sentence and splits it by spaces using a regular expression
        """
        ret = 0
        if type(text) is list:
            for t in text:
                ret +=len(re.sub('(\s+)','|-BJM-|',t).split("|-BJM-|"))
        elif type(text) is str:
            ret +=len(re.sub('(\s+)','|-BJM-|',text).split("|-BJM-|"))            
        return ret

    def summarize(obj, roles, prop):
        """
            summarize():    Meant to be somewhat general purpose, takes as input the debate object
            as well as the roles/people to be summarized by, as well as a property for summarizing.
            The property could very well be a function, built in like len() or custom.
        """
        revRole = {}
        ret = {}
        ### Reverse the roles object so that the names are keys and the role type is
        ###     the value, this way the loop through the statemens will be quick.
        
        for r in roles.keys():
            for p in roles[r]:
                revRole[p] = r
                
        ### Loop through the statements and assign each property value to the by
        ###     group revRole object values.
                
        for o in sorted(obj['sections'].keys()):
            for l in obj['sections'][o]:
                if l['SPEAKER'] in revRole:
                    #print '%s--%s(%s)|%f'   %(o,
                    #                        revRole[l['SPEAKER']],
                    #                        l['SPEAKER'],
                    #                        prop(l['STATEMENT']))
                    ret.setdefault(o,{})
                    ret[o].setdefault(revRole[l['SPEAKER']],0)
                    ret[o][revRole[l['SPEAKER']]] += prop(l['STATEMENT'])
        return ret

    def flatten(obj,akeys,filepath,delim):
        """
            flatten():  A function intended for exporting a results data object
            into a delimited file for excel, R, Stata oriented work.
        """
        lines = []
        for o in obj:
            string = ""
            for k in akeys:
                string += "%s%s" %(delim,k)
                if k in o:
                    if (type(o[k]) is list):
                        string += "%s%s" %(delim,delim.join(o[k]))                    
                    elif (type(o[k]) is dict):
                        for l in sorted(o[k].keys()):
                            string += "%s%s" %(delim,delim.join([l,str(o[k][l])]))                    
                    elif (type(o[k]) is str):
                        string += "%s%s" %(delim,o[k])                    
                else:
                    string += "%s%s" %(delim,"")
            string +="\n"
            print string
            lines.append(string)
        f = file(filepath,'wb')
        f.writelines(lines)
        f.close()


###### Correction object.  This object captures specific processing
    ##  instructions for each of the debate records.  The key for the object
    ##  is the filepath to the pickle object.
    ##
    ##  SECTIONS:   Key values are the time markers before the sections begin
    ##      values are the round titles
    ##  TITLE:      Title for the debate
    ##  SPEAKERS:   Correct the spelling for speaker names
    ##  ROLES:      Make sure all roles are properly assigned
    
    correctionObj = {'i2Debates/011514 obamacare.p':{
                            'title':'Obamacare is now beyond rescue',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE'],
                                     'for':['SCOTT GOTTLIEB']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'DR. SCOTT GOTTLIEB':'SCOTT GOTTLIEB'},
                            'sections':{
                                    '18:48:36':'R0-Audience Instructions',
                                    '18:54:02':'R1-Introduction',
                                    '19:00:02':'R2-Opening Statements',
                                    '19:30:03':'R3-Debate',
                                    '20:12:01':'R4-Closing Statements',
                                    '20:22:03':'R5-Conclusion',
                                }
                        },
                        'i2Debates/011613 israel iran.p':{
                            'title':'Israel can live with nuclear Iran',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '18:47:02':'R0-Audience Instructions',
                                    '18:51:01':'R1-Introduction',
                                    '18:59:00':'R2-Opening Statements',
                                    '19:29:51':'R3-Debate',
                                    '20:20:41':'R4-Closing Statements',
                                    '20:29:00':'R5-Conclusion',
                                }
                        },
                        'i2Debates/021313 genetic engineering.p':{
                            'title':'Prohibit genetically engineered babies',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'ROBERT WINSTON':'LORD ROBERT WINSTON'},
                            'sections':{
                                    '18:49:35':'R0-Audience Instructions',
                                    '18:52:06':'R1-Introduction',
                                    '18:58:51':'R2-Opening Statements',
                                    '19:29:09':'R3-Debate',
                                    '20:20:05':'R4-Closing Statements',
                                    '20:29:57':'R5-Conclusion',
                                }
                        },
                        'i2Debates/031313 strong dollar.p':{
                            'title':'America doesnt need a strong dollar policy',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '18:47:41':'R0-Audience Instructions',
                                    '18:53:04':'R1-Introduction',
                                    '18:59:05':'R2-Opening Statements',
                                    '19:28:00':'R3-Debate',
                                    '20:21:14':'R4-Closing Statements',
                                    '20:31:54':'R5-Conclusion',
                                }
                        },                                          
                        'i2Debates/041713 gop.p':{
                            'title':'The GOP must seize the center or die',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'RALPH REEDR':'RALPH REED'},
                            'sections':{
                                    '18:48:14':'R0-Audience Instructions',
                                    '18:52:12':'R1-Introduction',
                                    '18:57:13':'R2-Opening Statements',
                                    '19:12:19':'R3-Debate',
                                    '20:21:18':'R4-Closing Statements',
                                    '20:32:16':'R5-Conclusion',
                                }
                        },                                          
                        'i2Debates/061913 pentagon budget.p':{
                            'title':'Cutting the Pentagons budget is a gift to our enemies',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE'],
                                     'for':['ANDREW KREPINEVICH']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'REW KREPINEVICH':'ANDREW KREPINEVICH'},
                            'sections':{
                                    '17:33:29':'R0-Audience Instructions',
                                    '17:40:30':'R1-Introduction',
                                    '17:45:29':'R2-Opening Statements',
                                    '18:11:32':'R3-Debate',
                                    '18:53:34':'R4-Closing Statements',
                                    '19:05:30':'R5-Conclusion',
                                }
                        },                                          
                       'i2Debates/091013 drones.p':{
                            'title':'The US drone program is fatally flawed',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'ADMIRAL DENNIS BLAIR':'DENNIS BLAIR',
                                        'GENERAL NORTON SCHWARTZ':'NORTON SCHWARTZ'},
                            'sections':{
                                    '18:46:03':'R0-Audience Instructions',
                                    '18:51:04':'R1-Introduction',
                                    '18:57:58':'R2-Opening Statements',
                                    '19:27:09':'R3-Debate',
                                    '20:17:06':'R4-Closing Statements',
                                    '20:28:02':'R5-Conclusion',
                                }
                        }                                                               
                     };


###### Using the functions to access the data after having loaded
    ##  all of the appropriate modules, etc.
    
    ## Identify all of the pickle files associated with I2US debates
    debateFiles = ["%s/%s" %(debateDir,f) for f in os.listdir(debateDir+"/") if re.match(debateFilePattern,f)]

    ## Load a debate from its pickle file and return the turn taking frequency
    ##  by role and participant
    full=[]
    aKeys = []
    for d in debateFiles:
        if (d in correctionObj):
            ## Note that not all 22 files are read, merely the ones with correction keys
            debate = openDebate(filepath=d)
            debate = correctDebates(correction=correctionObj[d], obj=debate)
            speakerTurns = speakerTurnFrequencies(debate)
            print (d)
            pprint.pprint(speakerTurns)

            ret = {'title':debate['title'],
                   'before':debate['before'],
                   'after':debate['after']}
            ret.update(summarize(
                                      obj=debate,
                                      roles={'for':debate['for'],
                                             'against':debate['against']},
                                      prop=splitWords)
                                )
            full.append(ret)
            aKeys.extend(ret.keys())
            aKeys = list(set(aKeys))

    aKeys = sorted(aKeys)
    pprint.pprint(aKeys)
    flatten(obj=full,
            akeys=aKeys,
            filepath=r"return.txt",
            delim="|")

print('--end--');
