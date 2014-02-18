intelligence-squared
====================

# Objective
Competitive discourse is a hallmark of the human experience.  The intent of this project is two part: (**a**) to explore how we debate eachother, and (**b**) to develop new methodologies for studying and visualizing debates.  Since 2006 the Intelligence Squared US project (http://intelligencesquaredus.org/) has hosted many debates (83 as of January 2014) on relevant public policy concerns.  Guest debaters have included former Governors, ambassadors, as well as authors and scholars.  Unlike other debate shows Intelligence Squared polls the audience before and after each debate, which provides an interesting measure of argument effectiveness.  The python scripts, modules, and data here repository are meant to be used for Natural Language Processing (NLP) efforts to expose speaker sentiment, collaboration, and to provide annotations that might aid audience member comprehension of the sometimes jargon and fact riddled material.

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

### The PDF files
These were downloaded from the Intelligence Squared US website.  The python based scripts for scraping, processing the PDFs to HTML, then processing the HTML are not shared on the GitHub page, but if you are interested contact me and I am happy to share.

As more records are added to this folder the general data layout is subject to change, but ideally at a minimum.

## Get Started

The files *debateData.txt* and *debateResults.txt* include the primary data for all 22 debates.  Both use the delimiter *#*|*#* (smiley face with earmuffs), the first line of data are the variable headers.  The following will parse the files into NumPy Arrays, ready for analysis (this simple script is in *i2-sample.py*):

```python
    
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

```

In case you want to pre-process the results in some way (i.e., search the text for LIWC categories or affect the methods I used to split the text into sections) then you will want to run the *i2-getstarted.py* script.  I heavily commented the file, but in a nutshell the functions are provided to help manage the pickle data, summarizing elements of the text, managing LIWC or other dictionary based files, and returning the *debateData.txt* and *debateResults.txt* files. The python script *i2-getstarted.py* demonstrates how to open the pickle files and perform some very basic summaries of the data.  If you have recommendations or thoughts about how to improve the program, please don't hesitate.


-- Thanks, Brian
