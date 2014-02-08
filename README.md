intelligence-squared
====================

# Objective
Competitive discourse is a hallmark of the human experience.  The intent for this project is two part: (**a**) to explore how we debate eachother, and (**b**) to develop new methodologies for studying and visualizing debates.  Since 2006 the Intelligence Squared US project (http://intelligencesquaredus.org/) has hosted many debates (83 as of January 2014) on relevant public policy concerns.  Guest debaters have included former Governors, ambassadors, as well as authors and scholars.  Unlike other debate shows Intelligence Squared polls the audience before and after each debate, which provides research with an interesting measure of argument effectiveness.  The python scripts, modules, and data within this repository are meant to be used for Natural Language Processing (NLP) efforts to expose speaker sentiment, collaboration, and to provide annotations that might aid audience member comprehension of the sometimes jargon and fact riddled material.

# Folders and Files
A breakdown of what is in this repository and a few recommendations on how to get started.

## i2Debates (directory)
As of January 2014 the Intelligence Squared US project has hosted 83 debates.  Each debate is presented on their website with a tremendous amount of information about each participant, the issues discussed, as well as video and full-text transcripts covering the event.  Over time more of this material will be processed into pythonic friendly forms for computational work.  Currently the full text for 22 of the debates are shared.

### The pickle object has the following structure:
* Each debate object is a python **dict**
* The debate object has the following keys: **text**, **date**, **for**, **against**, **moderator**, **before**, and **after**
* **TEXT**:  An array of dictionaries, one array for each speaker turn in the debate.  The dictionaries include a range of keys, but always list the **SPEAKER** and the **STATEMENT**, but may include the **PAGE** (page number), **TIME** (hours, minutes, seconds) and **BREAK** (an audience interaction like laughter or applause).  It is important to note that the **STATEMENT** array provides the full-text by line which is an artifact of the Pdf2Txt process.  The other objects within the turn use numerical keys to represent the line in the statement afterwhich the non-statement event appears in the text.  For example, the a **BREAK** value {4:'[applause]'} means that the audience applaused after the 4th statement line during the speaker turn.
* **DATE**:  The date for the debate stored as a dictionary with values (month, day, year).
* **FOR / AGAINST / MODERATOR**:  The team of speakers assigned to each side of the debate.
* **BEFORE / AFTER**:  Audience polling results from before and after the debate

As more records are added to this folder the general data layout is subject to change, but ideally at a minimum.

## Get Started
A single script to download the data and begin processing.  The python script *i2-getstarted.py* demonstrates how to open the pickle files and perform some very basic summaries of the data.

```python
    debateDir = 'i2Debates'
    debateFilePattern = '.*[.]p$'

    ## Identify all of the pickle files associated with I2US debates
    debateFiles = ["%s/%s" %(debateDir,f) for f in os.listdir(debateDir+"/") if re.match(debateFilePattern,f)]

    ## Load a debate from its pickle file and return the turn taking frequency
    ##   by role and participant
    for d in debateFiles:
        debate = openDebate(filepath=d)
        speakerTurns = speakerTurnFrequencies(debate)
        print (d)
        pprint.pprint(speakerTurns)
```

Additionally, functions are offered to view the pickle debate object in the browser and edit/add to the data using a javascript/css GUI.  Finally, once the object has been edited using the GUI a final function is offered to save the updates to the pickle debate object.

> The reality of text oriented research is that these files are initially very messy and need cleaning.  While I could write scripts that clean them all, the effort would take a tremendous amount of time and accuracy would be limited to my own eyeballs on the files.  *Lets work together* to prepare the research files and then build some interesting NLP algorithms for exploring them.

-- Thanks, Brian
