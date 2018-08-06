# PerSieve

PerSieve is a Python package designed to put astronomical data in the browser for rapid visualisation and analysis.

### Important Caveats

**It is important to note that the codes supplied here are provided for completeness of the DWF code repository, but cannot usefully be run outside a specific environment, described below, and without access to the relevant database, which is not supplied in this repository. If you need access to the database, get in touch. 

Additionally, the codes are supplied for now as a completely unpolished spaghetti nightmare. A general, clean, code release is planned for late 2018. I would highly recommend holding off on any work with these scripts until then. If you really feel you must interact with these codes prior, please get in touch at sarah.hegarty22@gmail.com prior.** 

### Description 

For DWF, PerSieve is designed to give the user all the information they need to assess a transient candidate, and record their assessment. By putting these capabilities in the browser, we make sure that the tool can be used anywhere and at any time, without needing the user to install anything, or have access to a particular software environment.

At the user's end, PerSieve simply generates a web page. At the time of writing, the website has three tabs: an introduction/login tab, a summary tab showing a data table of detected candidates, and the main tab, where candidate images and associated plots are shown, along with feedback buttons etc. Please see the associated PerSieve "introduction" pdf for more details on the page contents. 

To achieve this, the 'bokeh' package is used (https://bokeh.pydata.org/en/0.12.4/). Bokeh wraps JS capabities into Python, making it possible to generate interactive web graphics. Additionally, it allows you to create your own 'bokeh' server instances, so that the pages you create can be viewed by the general user via websocket. More details on running bokeh servers are available at https://bokeh.pydata.org/en/0.12.4/docs/user\_guide/server.html.

Thus, although PerSieve scripts are written in Python, they are **not** run using Python. Instead, we serve them using bokeh, as follows. The details of this command are discussed below.

'bokeh serve DWF\_web\_portal\_v3.py --port 5102 --host 127.0.0.1:80 --host webprojects.hpc.swin.edu.au:80'

This command launches a bokeh server, serving the page which is described in DWF\_web\_portal\_v3.py. Until a kill command is received, this server will listen for connections at webprojects.hpc.swin.edu.au/DWF\_web\_portal\_v3/. Each connection will launch a page instance. All the figures and the page layout are initialised when the instance is: see functions initialise\_introduction\_tab, initialise\_summary\_tab, and intialise\_candidate\_plots.

Upon connection, the user has to log in with an approved user ID and password (**important: password handling is (for now) rudimentary at best. Everything is plaintext, there is one general-purpose password for everyone, and nothing is encrypted. This may keep a casual browser from being able to view any data, but it should absolutely not be trusted as any sort of genuine security measure.**). Once they hit the "show me some data" button (aka "master start" button), the function 'ms\_button\_pressed' is called. This checks their credentials, and calls 'next\_button\_callback'.

As the code is currently structured (poorly), the latter is the most important function in the code. It updates the data shown on the "candidate viewer" tab, and writes to db any assessments the user has made.

When it is *first* called, upon a master start button press, this function also calls 'prepare\_candidates\_from\_db'. This function performs a database call to compile the list of candidates that the user will be presented for assessment. As DWF is a dynamic environment, the criteria for what candidates you want the user to see may change. So, the database call that will determine what users see lives in a separate file: TLPT.txt. This file will be checked *every time* the user hits the master start button; so, by editing it on-the-fly, you can control what the users are shown, how many candidates they are shown at a time, etc. For example, as uploaded today, TLPT.txt contains the call:

'Id>35011 and mary\_priority > 0 and prev\_user\_ratings <1 and my\_priority =-1 order by mary\_priority desc limit 200'

This will call all candidates past a certain ID number cutoff, which *Mary* has prioritised, and nobody has yet rated (see below for distinction between mary\_priority and my\_priority). It will then show them 200 at a time, in descending order of Mary rating (ie, most interesting first). But, if you are running things, alter this file as need be, on the fly, using PostgreSQL syntax, to control what is shown.

There is an analogous file - LPT.txt - which controls what is shown in the summary data table. At present, and in general, this just says to pull all candidates with ID>1 (ie all candidates), but you may wish to alter this. 

Once the list of candidates meeting your TLPT condition (ie, those to be assessed) is pulled from the database, it lives as current\_session.candidate\_list, a list of *where to find the data* for each candidate in turn, and perhaps more usefully as current\_session.idnos, a list of the Id numbers to be assessed. 

Iterating through this list, the data for each candidate is pulled (using get\_all\_ID\_arrays\_from\_fits(candidate\_filename)) and displayed, in turn. This is reasonably rapid, since it takes advantage of a capability in bokeh to *update* the data that each plot uses, rather than re-generating the whole figure from scratch. Rather than re-drawing each figure for each new candidate, all the figures and their type of content (eg lines, image arrays, points) are defined at page load by initialise\_candidate\_plots, but initialised to zeroes or nulls. Then I simply update the data that each plotting feature (referred to in bokeh as a glyph) references, each time I want to show a new candidate. 

Once a candidate has been displayed, the user can interact with it using the little toolbar attached to each plot, and make their assessment with the buttons or notebox (if they make no assessment/rating, I record a rating of zero. Otherwise, like *Mary*, the ratings go from 5 (best) to 1 (worst), corresponding to the  five buttons. The 'asteroid' button gives a rating of -5). Then when they click 'next', the data updates to the next candidate (iteration is tracked throughout the code using 'candidate\_index' and 'current\_index' (see below)), and their assessment is recorded. This continues until they exceed the length of the list of candidates prepared for assessment, at which time they are returned to the introduction tab, and can start again on a new list by pressing master start. 

As these assessments are being made, anyone on a parallel session of PerSieve can keep track of progress **and, importantly, see which candidates have been identified as the most interesting** in the summary tab. They have to press the button to get a fully up-to-date data pull, but once this is done a semi-interactive data table is displayed. You can sort the columns with a click on the header to help you find whatever you are interested in. Then, type the ID numbers of anything interesting in at the box at the bottom, or (for more robust results), the box on the introduction tab, and click through to see the data. 

In this way, a team of volunteers can work through DWF data in a reasonably rapid manner, and we have an up-to-the-minute record of what they thought was interesting or not. 

### Auxilary codes

For real-time DWF runs, there are a few auxilary Python scripts which should be started alongside the Bokeh server. Each of these is set up so that, once started, they run continuously until a kill signal is received, checking every minute or so for new information. They all act to keep the database up-to-date in different ways.

* 'pg\_crossmatcher.py'. 
This code is authored by Antonino Cucchiara, and his student Chris Murphy, at the University of the Virgin Islands. I have made only superficial modifications. Every few minutes, it checks the database for candidates which have *not* had their positions cross-matched against (an)other catalogue(s). If it finds any, it checks specified catalogues for any objects within a specified radial distance of their position. Matches that are found are logged to the database. This information is later displayed in the web page, in the small text table below a candidates data plots. It may help people make a decision.

Start this code at the command line with 'python pg\_crossmatcher.py'. The crossmatch is not super fast, so can take a while if a lot of candidates need matching; however, when new *Mary* runs come in, many of the candidate Id numbers will have been detected and crossmatched before. In this case, we don't run the crossmatch again, but just take previous result.

* 'pg\_incoming\_data\_monitor.py'. 
This code monitors the incoming data location (defined as 'base\_path') for new masterlists. It checks every 20 seconds for masterlists not seen before. If it finds some, it parses them and populates the database accordingly. There is a toggle in this code (line 204) which you can toggle on if you want to build your database from scratch; otherwise it updates the existing database. Look here if you need to know what the table variable names are. Start this code with 'python pg\_incoming\_data\_monitor.py'. Start it when you start the bokeh server, and don't restart it during a real-time run, unless you code in some logic to not duplicate data that is already in the database. 

* 'pg\_calculate\_priorities\_new.py' 
This code monitors the database, and attempts to prioritise candidates for assessment in a dynamic and continuous manner. There is a column in the database for tracking this - it is called my\_priority. I have tried various approaches to prioritising the candidates, based on a combination of the candidate's: *Mary* priority, time of detection, number of detections, crossmatch results, number of previous assessments, results of any previous assessments, length of time waiting to be assessed, etc. However, this has proved hard to get right: the correct priortisation scheme for any given moment is heavily dependent on the status and progress of the observations, and the progress of the assessors. So, for now, this prioritiser just sets my\_priority to -1 for the *newest* detection of each candidate, and to -2 for *older* detections. Then, the database query in TLPT.txt is written to pull only where my\_priority>=-1, ensuring only the newest data on any candidate is used for assessments. Run this code at command line like the others. 

### Server environment

Because our data lives on the supercomputers, and the supercomputers have sensible internet access controls, it is not completely straightforward to run PerSieve in a place where it can both a) see the DWF data and b) see the outside world. 

I have wrangled such a set up via IT and with the excellent help of Amr Hassan (Monash). To summarise: I run a VM (Open Stack) with web access on g2 (can be ported to ozstar if/when g2 is decommissioned). I have the OzStar DWF project data folder (/fred/oz100/) mounted here. IT have opened some ports, so I can run my bokeh server (behind Apache) and have the pages be accessible to the outside world.

Alongside this, I run a Postgres database, which is only accessible internally.

This VM is accessible just by ssh, but I am under pretty strict instructions about sharing the access credentials. I will pass these on at the conclusion of my PhD, but if you think you need them before the end of 2018, please email.

Another note is that, normally, during a DWF run, I would run multiple bokeh servers, starting them with a bash script like this:

'#!/bin/bash

bokeh serve DWF\_web\_portal\_v1.py --port 5100 --host 127.0.0.1:80 --host webprojects.hpc.swin.edu.au:80 &

bokeh serve DWF\_web\_portal\_v2.py --port 5101 --host 127.0.0.1:80 --host webprojects.hpc.swin.edu.au:80 &

bokeh serve DWF\_web\_portal\_v3.py --port 5102 --host 127.0.0.1:80 --host webprojects.hpc.swin.edu.au:80 &'

These three versions of the parent script can be identical, to help spread out the load when many users are active (I have never had a problem with load unbalance in the current setup, but it doesn't hurt to take a precaution). Or, if you want to show some users a slightly different version to others, just alter one of the scripts).


### Other notes

* **Important:** this code has been developed for DWF using Bokeh version 0.12.4. Newer versions are now available, but they are *not* interoperable. 

* This code has been developed with the aim of being as much of a "one-stop shop" as possible for assessing the candidates. Accordingly, we have often discussed putting the data for more than one candidate in the browser at once. Imagine the usual layout, but (for example) making the page much longer, or wider: then if you consider the square region enclosing all the plots etc for *one* candidate as a "unit", you can envisage fitting multiple "candidate units" on one page, one below the other (or next to each other, etc).

For a person with a large enough screen, this might be a more useful or quicker way to look through multiple candidates, instead of clicking through them one by one. So, I have developed PerSieve with the goal of layout flexibility: if you edit the code to set variables session.nrows and session.mcols, you can dictate that the page layout has a grid of n rows of units, and m columns of units. *However*: I have found that the current 1x1 layout (ie, one candidate at a time) actually works well. Even for one candidate, the amount of information displayed is significant, and I suspect we will rapidly get decreasing returns by displaying more. Also, not many people have a screen big enough for multiple candidates at once to be a time-saver. *Most importantly*, though, my studies of how users use PerSieve show that the current set up is actually a very efficient way for people to interact with this data. 

Accordingly, nxm layouts have not been tested in a real DWF run. And, as much development has occured since they were last used at all, I do not guarantee that changing these variables won't break something else - so, I would advise against it on the whole.

* A trap for the unwary: typically, the naming convention for the DWF data files may change between DWF runs. For example, '8hr\_180608\_mrt1\_94.masterlist.txt' is one file name. The field name, date, and mary run number are all free to change within a DWF run, and PerSieve knows how to parse these names, so that is fine. But *between* runs, people earlier in the pipeline may choose to alter the identifier which is here 'mrt1', changing it to (eg) mNOAO5, or anything else helpful. Unfortunately, any change to this name means you need to change the hardcoded line 735 in DWF\_web\_portal\_v3.py to reflect the new convention. Will fix this in next version of the code. 

* Other traps for the unwary undoubtedly exist in the code as it stands at present. Read and use at your own risk, and try not to judge me too harshly!

## Summary of database columns for table 'candidates':

* Id: candidate Id number assigned by Mary. Integer
* field: the observing field. Text.
* obsdate: the observing date. Integer.
* notes: any notes people have added (cumulative; semicolon-separated list). Text.
* ratings: any numerical ratings people have given (cumulative; semicolon-separated list). Text.
* checktimes: the timestamps of any ratings people have given (cumulative, semicolon-separated list). Text.
* checkedby: the identifiers of anyone who has rated the object (cumulative, semicolon-separated list). Text.
* magnitude: magnitude, from masterlist. Float.
* mag\_err: error in the magnitude, from masterlist. Float.
* mary: mary run where detected. Text.
* ccd: the ccd where detected. Integer.
* cand: the cand number on that ccd. Integer.
* sent: a container to indicate whether the candidate has been sent for assessment. Currently unused. Integer. 
* average\_rating: average of any ratings conducted. Float. 
* mary\_priority: rating assigned by Mary. From masterlist. Integer.
* my\_priority: a rating to help prioritise candidate. Generated in incoming data monitor, and described above. Integer. 
* n\_detections: number of times the candidate has been detected. Integer.
* prev\_user\_ratings: a count of the number of previous ratings. Integer.
* ra: right ascension, from masterlist. Float.
* dec: declination, from masterlist. Float.
* crossmatch: string returned by crossmatch. Note, full crossmatch result stored in another table, crossmatch\_data. Text. 
* matched: A boolean indicating whether a crossmatch has been performed for this candidate yet. Integer.
* masterlist\_name: name of the associated masterlist. Text.
* clist\_entry: moderately redundant string indicating where to find masterlist+stamps. Text. 
* n\_matches: number of known objects found by crossmatch. Integer.
* t\_detection: time of detection. NOTE: this is really 'time of addition to the database'. For realtime work, they should be no more than 30s separated, but beware otherwise. Note that mary run id is also a proxy for time. 
* matchtype: integer indicating what the result of crossmatch was. Integer. Maybe unused.
* matchsep: separation of closest crossmatch (in arcsec). Float. Maybe unused.

