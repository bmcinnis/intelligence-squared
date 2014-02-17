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

mods = ['os','pprint','pickle','re','numpy']
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
    import os, pprint, pickle, re, numpy

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

            The TITLE block simply creates a title key, the value provided by the correction
            object.

            The ROLES block adds name spellings to the roles key for the debate object.
            This is important because for some of the debates the transcription firm
            provides multiple spelling forms for the same participants.

            The SPEAKERS block corrects name misspellings.

            The SECTIONS block divides the text into debate sections based on time stamps
            throughout the document.

            Finally, the POLL results are tranformed from string to numerical values in a
            nested dictionary.  Delta values (e.g., after - before) are offered.
        """
            
        ##  Process any elements from the correction dictionary
        for c in correction.keys():
            if (c == "title"):
                print '----Title: '+correction[c]
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
                                tLine = l['STATEMENT'][0:int(fBreak)-1]
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

        ##  Clean the before and after polling results and introduce the delta
        poll_results = ['before','after']
        poll_types = []
        poll = {}
        for p in poll_results:
            if p in obj:
                poll.setdefault(p,{})                
                for r in obj[p]:
                    match = re.match('^(?P<perc>[0-9.]+)[%][\s-]*(?P<type>[A-z]+)$',r)
                    if(match):
                        mgroup = match.groupdict()
                        poll[p][mgroup['type'].lower()] = float(mgroup['perc'])
                        poll_types.append(mgroup['type'].lower())
        poll_types = list(set(poll_types))
        poll['delta'] = {}
        for t in poll_types:            
            poll['delta'][t] = poll['after'][t] - poll['before'][t]
                    
        print '----POLL Results:'
        pprint.pprint(poll)
        obj['poll'] = poll

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

    def arrayTraversal(obj,depth):
        """
            arrayTraversal():   Recursive function to identify the values of nested elements
        """
        if ((type(depth) is list):
            first = depth[0]
            if first in obj:
                print obj[first]
                depth.pop(0)
                return arrayTraversal(obj[first],depth)
            else:
                print 'Error: "'+first+'" does not exist'
        else:
            print 'Found: '+ obj[depth]
            return obj[depth]
            

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

    def flatten(obj,variables):
        variables ="" 
    

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
                        },                                                               
                       'i2Debates/091212superpacs.p':{
                            'title':'Two cheers for super PACS: Money in politics is still overregulated',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '18:47:11':'R0-Audience Instructions',
                                    '18:51:12':'R1-Introduction',
                                    '18:57:10':'R2-Opening Statements',
                                    '19:28:14':'R3-Debate',
                                    '20:21:15':'R4-Closing Statements',
                                    '20:31:16':'R5-Conclusion',
                                }
                        },                                                               
                       'i2Debates/101012rationinghealthcare.p':{
                            'title':'Ration end-of-life care',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '19:29:07':'R0-Audience Instructions',
                                    '19:39:04':'R1-Introduction',
                                    '19:45:02':'R2-Opening Statements',
                                    '20:15:59':'R3-Debate',
                                    '21:14:56':'R4-Closing Statements',
                                    '21:24:06':'R5-Conclusion',
                                }
                        },                                                               
                       'i2Debates/101613 big banks.p':{
                            'title':'Break up the big banks',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '18:49:35':'R0-Audience Instructions',
                                    '18:54:00':'R1-Introduction',
                                    '19:01:04':'R2-Opening Statements',
                                    '19:30:57':'R3-Debate',
                                    '20:19:00':'R4-Closing Statements',
                                    '20:27:00':'R5-Conclusion',
                                }
                        },                                                               
                       'i2Debates/101813 red state.p':{
                            'title':'For a better future, live in a red state',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '12:00:00':'R0-Audience Instructions',
                                    '12:11:52':'R1-Introduction',
                                    '12:16:57':'R2-Opening Statements',
                                    '12:40:56':'R3-Debate',
                                    '13:30:59':'R4-Closing Statements',
                                    '13:38:02':'R5-Conclusion',
                                }
                        },                                                               
                       'i2Debates/102412 taxes.p':{
                            'title':'The rich are taxed enough',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE'],
                                     'against':['MARK ZANDI']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'ART LAFFER':'ARTHUR LAFFER'},
                            'sections':{
                                    '18:52:02':'R0-Audience Instructions',
                                    '18:56:55':'R1-Introduction',
                                    '19:02:59':'R2-Opening Statements',
                                    '19:32:56':'R3-Debate',
                                    '20:28:54':'R4-Closing Statements',
                                    '20:36:51':'R5-Conclusion',
                                }
                        },
                       'i2Debates/111412 drugs.p':{
                            'title':'Legalize drugs',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '18:48:51':'R0-Audience Instructions',
                                    '18:53:11':'R1-Introduction',
                                    '18:58:06':'R2-Opening Statements',
                                    '19:28:57':'R3-Debate',
                                    '20:22:00':'R4-Closing Statements',
                                    '20:30:47':'R5-Conclusion',
                                }
                        },                     
                       'i2Debates/111413 guns.p':{
                            'title':'The constitutional right to bear arms has outlived its usefulness',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE'],
                                     'for':['ALAN DERSHOWITZ']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'ALAN DERSHOWITZ':'ALAN DERSHOWITZ',
                                        'EUGENE VOLOH':'EUGENE VOLOKH'},
                            'sections':{
                                    '18:48:32':'R0-Audience Instructions',
                                    '18:51:59':'R1-Introduction',
                                    '18:57:59':'R2-Opening Statements',
                                    '19:29:58':'R3-Debate',
                                    '20:21:08':'R4-Closing Statements',
                                    '20:32:00':'R5-Conclusion',
                                }
                        },                     
                       'i2Debates/112013 nsa.p':{
                            'title':'Spy on me, Id rather be safe',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '17:36:03':'R0-Audience Instructions',
                                    '17:39:07':'R1-Introduction',
                                    '17:44:04':'R2-Opening Statements',
                                    '18:11:05':'R3-Debate',
                                    '18:50:05':'R4-Closing Statements',
                                    '18:59:11':'R5-Conclusion',
                                }
                        },                     
                       'i2Debates/china-transcript.p':{
                            'title':'China does capitalism better than America',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '18:48:30':'R0-Audience Instructions',
                                    '18:51:38':'R1-Introduction',
                                    '18:58:37':'R2-Opening Statements',
                                    '19:29:36':'R3-Debate',
                                    '20:20:37':'R4-Closing Statements',
                                    '20:30:36':'R5-Conclusion',
                                }
                        },                     
                       'i2Debates/college.p':{
                            'title':'Too many kids go to college',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '19:50:51':'R0-Audience Instructions',
                                    '19:54:52':'R1-Introduction',
                                    '19:57:54':'R2-Opening Statements',
                                    '20:30:54':'R3-Debate',
                                    '21:18:53':'R4-Closing Statements',
                                    '21:27:55':'R5-Conclusion',
                                }
                        },                     
                       'i2Debates/internet-politics.p':{
                            'title':'When it comes to politics, the internet is closing our minds',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '18:45:42':'R0-Audience Instructions',
                                    '18:49:43':'R1-Introduction',
                                    '18:55:41':'R2-Opening Statements',
                                    '19:24:48':'R3-Debate',
                                    '20:18:47':'R4-Closing Statements',
                                    '20:28:48':'R5-Conclusion',
                                }
                        },                     
                      'i2Debates/men-are-finished.p':{
                            'title':'Men are finished',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'JON DONVAN':'JOHN DONVAN',
                                        'MALE ZINCZENKO':'DAVID ZINCZENKO'},
                            'sections':{
                                    '18:47:18':'R0-Audience Instructions',
                                    '18:50:17':'R1-Introduction',
                                    '18:52:16':'R2-Opening Statements',
                                    '19:25:16':'R3-Debate',
                                    '20:23:17':'R4-Closing Statements',
                                    '20:33:16':'R5-Conclusion',
                                }
                        },                     
                      'i2Debates/obama-jobs-act.p':{
                            'title':'Congress should pass Obamas jobs act - piece by piece',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE'],
                                     'for':['MARK ZANDI']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'JON DONVAN':'JOHN DONVAN',
                                        'MARK Z':'MARK ZANDI'},
                            'sections':{
                                    '18:44:53':'R0-Audience Instructions',
                                    '18:48:54':'R1-Introduction',
                                    '18:51:57':'R2-Opening Statements',
                                    '19:23:56':'R3-Debate',
                                    '20:17:52':'R4-Closing Statements',
                                    '20:27:54':'R5-Conclusion',
                                }
                        },                     
                      'i2Debates/obamacare.p':{
                            'title':'Repeal Obamacare',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE','RESULTS']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'JON DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '18:50:21':'R0-Audience Instructions',
                                    '18:55:25':'R1-Introduction',
                                    '18:56:20':'R2-Opening Statements',
                                    '19:29:26':'R3-Debate',
                                    '20:23:24':'R4-Closing Statements',
                                    '20:33:22':'R5-Conclusion',
                                }
                        },                     
                      'i2Debates/palestine.p':{
                            'title':'The UN should admit Palestine as a full member state',
                            'roles':{'moderator':['ROBERT ROSENKRANZ','PREAMBLE','RESULTS']},
                            'speakers':{'JOHN JOHN DONVAN':'JOHN DONVAN',
                                        'JON DONVAN':'JOHN DONVAN'},
                            'sections':{
                                    '18:51:41':'R0-Audience Instructions',
                                    '18:55:44':'R1-Introduction',
                                    '19:00:40':'R2-Opening Statements',
                                    '19:32:42':'R3-Debate',
                                    '20:26:42':'R4-Closing Statements',
                                    '20:37:45':'R5-Conclusion',
                                }
                        }                                            
                     };


###### Using the functions to access the data after having loaded
    ##  all of the appropriate modules, etc.
    
    ## Identify all of the pickle files associated with I2US debates
    debateFiles = ["%s/%s" %(debateDir,f) for f in os.listdir(debateDir+"/") if re.match(debateFilePattern,f)]

    ## Load a debate from its pickle file and return the turn taking frequency
    ##  by role and participant
    full={}
    aKeys = []
    for d in debateFiles:
        ## Note that not all 22 files are read, merely the ones with correction keys
        debate = openDebate(filepath=d)
        if (d in correctionObj):
            debate = correctDebates(correction=correctionObj[d], obj=debate)

            ret = {'title':debate['title'],
                   'before':debate['before'],
                   'after':debate['after']}
            
            ret.update(summarize(
                                      obj=debate,
                                      roles={'for':debate['for'],
                                             'against':debate['against']},
                                      prop=splitWords)
                                )

            full[d]=debate
            aKeys.extend(ret.keys())
            aKeys = list(set(aKeys))

        speakerTurns = speakerTurnFrequencies(debate)
        print (d)
        pprint.pprint(speakerTurns)
        

print('--end--');
