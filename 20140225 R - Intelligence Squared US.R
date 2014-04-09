## Intelligence Squared US (I2US)
## 2014-02-25 Brian McInnis (Last update: 2014-04-04)
## Objective:  Depict turntaking during debate section (R3)
 #  by LIWC function word categories (as percent of statement words)
 #  also showing Opening Statement and Closing Statements as
 #  baseline.

## Note on the commenting scheme:
 #  In most cases the questions/steps were written before any of the
 #  R script, and for that reason there's an odd commenting scheme.
 #  The first large blocks of code are devoted to building up the
 #  local dataset so that we can do some work on it.  The remainder
 #  of the script is commented with the following question-answer
 #  pattern.  You will see blocks of questions:  (1) Q1, (2) Q2, etc.
 #  followed by blocks of steps in answering the questions: [1.a], 
 #  [1.b], for question 1 and [2.a], [2.b] for question 2.

## Clear memory
 #  Quite likely you will need to run this program twice,
 #  Clearing the memory each time to build both the DR and DD
 #  Objects.  This is mainly because the full text is included.

rm(list = ls());

## Install and load any necessary packages
pack <- c('plyr','doBy','xlsx','XLConnect','ggplot2','data.table','reshape','tm', 'topicmodels');
for (p in pack) {
  print(p);
  if(p %in% rownames(installed.packages()) == FALSE){
    install.packages(p);
  }  
  if(p %in% rownames(installed.packages()) == TRUE){
    require(p,character.only=TRUE);
  }
}
rm(p,pack);

## Create the I2US Environment
setwd('/Users/bjm277/code/intelligence-squared/')
lf<-list.files(pattern = '^i2us[.]rda[ta]*$',
           ignore.case = TRUE);

if (length(lf)==0) {
  i2us <- new.env();
  ## Load XLSX libraries
  require(xlsx);
  options(java.parameters = "-Xmx1024m")
  require(XLConnect)  
  rm(lf);
}else{
  load(lf[1]);
  rm(lf);
}

## Using XLSX read the I2US results to memory as a dataframe (14 variables, 21 obs.)
if (exists("dr",where=i2us)==FALSE){
  dr<-read.xlsx(
                file='debateData (2014-02-22).xlsx',
                sheetName='Results'
  );  
  assign("dr", dr, envir = i2us);
  ## Save the i2us environment to the working directory
  save(i2us, file = "i2us.RData");
  rm(dr);
}

if (exists("dd",where=i2us)==FALSE){
  ## Using XLSX read the I2US data to memory as a dataframe (73 variables, 6,024 obs.)
  #  This takes a while because the statement strings are very long.
  dd<-read.xlsx(
              file='debateData (2014-02-22).xlsx',
#              sheetName='DDwoStatement'
              sheetName='DebateData'
  );
  assign("dd", dd, envir = i2us);
  ## Save the i2us environment to the working directory
  save(i2us, file = "i2us.RData");
  rm(dd);
}

## At this point the i2us environment is loaded, whether by opening
 #  the XLSX files and reading them in, or merely reopening the environment
 #  from the working directory.  Now, perform some quick checks on the
 #  data before producing the LIWC percentages and a ggplot to display them
 #  by debate and speaker turn.

attach(i2us);

## Explore the dataset a little bit:
 # (1) Does one side generally win the debate?
 # (2) What is the average margin of victory?
 # (3) Does the side that talks more win?

 ## [1.a:  Create outcome and margin variables to indicate which side won the debate]
  dr$outcome[(dr$poll.delta.against>dr$poll.delta.for)]<-1;
  dr$outcome[(dr$poll.delta.against<dr$poll.delta.for)]<-(-1);
  dr$outcome[(dr$outcome==NA)]<-0;
  dr$outcome<-as.numeric(dr$outcome);
  
  dr$persuadable<-(dr$poll.before.undecided-dr$poll.after.undecided);
  dr$margin.abs<-(dr$poll.after.for-dr$poll.after.against);
  dr$margin.delta<-(dr$poll.delta.for-dr$poll.delta.against);

 ## [1.b:  Tabulate by outcome and then by margin]
  addmargins(xtabs(formula=~title+outcome, data=dr),1);
  # (21 files) 11/10 (52.3% AGAINST vs. FOR)
  summaryBy(formula=poll.before.undecided~outcome, data=dr, FUN=c(mean,median));
  # (21 files) A little less than a THIRD of the audience is undecided ahead of a debate
  summaryBy(formula=poll.after.undecided~outcome, data=dr, FUN=c(mean,median));
  # (21 files) After the debate about 8% remain undecided, meaning that on avg. 22% of the audience is persuadable
  
  summaryBy(formula=persuadable~outcome, data=dr, FUN=c(mean,median));
  # (21 files) 22-24% on avg. are persuaded through the debate, assuming that the
  #   Audience members with existing opinions do not change their vote.

  summaryBy(formula=poll.delta.against~outcome, data=dr, FUN=c(mean,median));
  summaryBy(formula=poll.delta.for~outcome, data=dr, FUN=c(mean,median));
  # (21 files) Though we don't know whether there is back and forth within the
  #   populations with existing opinions, neither side appears to lose support
  #   regardless of who wins a debate.
 
  summaryBy(formula=margin.abs~outcome, data=dr, FUN=c(mean,median));
  # (21 files) The margin of victory (by audience final polling) is on avg. 34-35%
  summaryBy(formula=margin.delta~outcome, data=dr, FUN=c(mean,median));
  # (21 files) The margin of victory (by delta) is between 14 and 22%

  cor.test(formula=~outcome+poll.before.for,data=dr);
  cor.test(formula=~outcome+poll.before.against,data=dr);
  cor.test(formula=~outcome+poll.before.undecided,data=dr);
  cor.test(formula=~outcome+persuadable,data=dr);


## Convert LIWC scores to percentages
# (1) Identify all of the LIWC variables of interest
titles <- unique(dd$title)
liwc<-grep(pattern='^liwcScores[.](?!total).*$', 
                   x=names(dd), 
                   ignore.case = TRUE, 
                   perl = TRUE, 
                   value = TRUE);

## LSM:  Linguistic Style Matching
## Based on 9 LIWC:  articles, common adverbs, personal pronouns, indefinite pronouns, prepositions, negations, conjunctions, and quantifiers

liwc<-c("liwcScores.Article","liwcScores.Adverbs","liwcScores.Posemo","liwcScores.Ppron","liwcScores.Ipron","liwcScores.Prep","liwcScores.Negate","liwcScores.Conj","liwcScores.Quant");
basic<-c("line","title","file","section","role","speaker");
totals<-c("liwcScores.total.words","liwcScores.total.sentences");
dd.liwc <- dd[,names(dd) %in% c(basic,liwc,totals)];

## Create the LIWC percentages
#   The function eLIWC creates a rolling average LIWC score, this is so that
#   when calculating the LSM (Linguistic Style Matching), each exchange will
#   represent the average LSM at that point (based on all prior exchanges).
#   Most papers aggregate at the experience or document level, the rolling
#   approach is to eventually see if there's a way to predict an outcome 
#   based on early exchanges.

## DDPLY (part of the PLYR package) is used to create by group LIWC calculations.
#   Here LIWC scores are generated by title.

eLIWC <- function(x){
  print(x[1,"title"]);
  for (i in 1:nrow(x)) {
    for (t in liwc){
      #print(paste('---',t,sep=""));
      #ROLLING AVERAGE x[i,paste("perc.",t,sep="")] <-(sum(x[seq(from=1,to=i),t])/sum(x[seq(from=1,to=i),"liwcScores.total.words"]))*100;
      x[,paste("perc.",t,sep="")] <-(x[,t]/x[,"liwcScores.total.words"])*100;
    }
  }
  return(x);
};
dd.liwc<-ddply(dd.liwc,.(title,section,speaker), eLIWC);
dd.liwc<-dd.liwc[with(dd.liwc, order(title, line)), ]


## The ePairing function identifies the next speaker and their role in the debate.
#   Additionally, the speakingOrder variable is created so that summaries (i.e., LSM)
#   can be made based on who is speaking to whom.

## Here DDPLY aggregates the results by title and by section in order to isolate the
#   debate portion of the show.

ePairing <- function(x){
  ## Return the prior value for each speaker
  ids<-c("speaker","role");
  for (t in ids){ 
    x[,paste("p.",t,sep="")] <- c(rep(NA,1),head(as.character(x[,t]),-1));
    summary(x[3,c(t,paste("p.",t,sep=""))]);
  }
  x[,"speakingOrder"]<-paste(x$role,x$p.role,sep="<-");
  return(x);
}
dd.lsm<-ddply(dd.liwc,.(title,section), ePairing);

## eLSM calculates the LSM
#
eLSM <- function(x){
  for (t in c(paste("perc.",liwc,sep=""))){
    x[,paste("p.",t,sep="")] <- c(rep(0.0001,1),head(as.numeric(x[,t]),-1));
    # (Ireland, 2010)  Add + 0.0001 to the denominator to prevent empty sets
    # http://pss.sagepub.com.proxy.library.cornell.edu/content/22/1/39.full.pdf
    x[,paste("lsm.",t,sep="")] <- as.numeric(1-(abs(x[,paste("p.",t,sep="")] - x[,t])/(x[,paste("p.",t,sep="")] + x[,t] + 0.0001)));
    #print(summary(dd.liwc[,c(t,paste("p.",t,sep=""),paste("lsm.",t,sep=""))]));
  }
  for (i in 1:nrow(x)){
    x[i,"lsm"]<-sum(x[i,c(paste("lsm.",paste("perc.",liwc,sep=""),sep=""))])/length(liwc);    
  }
  return(x);
}
dd.lsm<-ddply(dd.lsm,.(title,section,speakingOrder), eLSM);


eNumber <- function(x){
  for (i in 1:nrow(x)){
    x[i,"bin"]<-floor(i/5);    
    x[i,"line.bin"]<-i;    
  }
  return(x);
}
dd.lsm<-ddply(dd.lsm,.(title,section,role), eNumber);


## Create several GGPLOTs to depict the LSM by utterance during the debate section
for (t in titles){
  print(t);
  #tsub <- subset(dd.lsm,(title==t)&((speakingOrder=="against<-for")|(speakingOrder=="for<-against")|(speakingOrder=="for<-moderator")|(speakingOrder=="against<-moderator"))&((section=="R3")));
  tsub <- subset(dd.lsm,(title==t)&((speakingOrder=="against<-for")|(speakingOrder=="for<-against"))&((section=="R3")));
  lSect <- aggregate(.~section,
                     data=tsub[,c("line","section")],
                     FUN=min)
  p <- ggplot(data=tsub,
              aes(x=line, 
                  colour=factor(role),
                  y=lsm),
                  group=factor(bin))+
    labs(title = paste("I2US Debate: ",t,sep=""), x = "By utterance (within Debate Section)", y = "Linguistic Style Matching (LSM)")+
    geom_point()+
    geom_line()+
    stat_smooth(method = "lm");

  ggsave(plot=p, filename=paste("images/",t,".png",sep=""));
  print(p);
}

### Commented out below is work in progress:
## Topic Models:
#   Provides access to LDA by David Blei: http://cran.r-project.org/web/packages/topicmodels/topicmodels.pdf
#   (1) Create the term document matrix based on the statement data

dd$rNames = paste(dd$file, dd$line, sep="_");
dd.statement <- data.frame(docs=dd[,"statement"],row.names = c(dd[,"rNames"]));
dd.statement <- DataframeSource(x=dd.statement);
#inspect(Corpus(dd.statement))
dd.tm <- DocumentTermMatrix(Corpus(dd.statement),control = list(removePunctuation = TRUE,
                                                                tolower = TRUE));
## Add meta data values to the TDM
meta(dd.tm, '');

#findFreqTerms(dd.tm, 5);
#findAssocs(dd.tm, "war", 0.5);
#rowTotals <- data.frame(apply(dd.tm , 1, sum));
#lda<-LDA(x=dd.tm, k=2);


## Merge the DD with DR
#dm<-merge(x=dd.liwc,
#          y=dr,
#          by=c("file"));






#####

detach(i2us);
save(i2us, file = "i2us.RData");
print("--end--");