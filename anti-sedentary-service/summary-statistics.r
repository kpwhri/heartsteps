## DRAG IN ALL DATA FOR PEOPLE 
## MANUAL LIST OF TEST PARTICIPANTS
## Numbers = "REAL PEOPLE"
## "Test-XXXX" = "FAKE PERSON" (e.g., peng, walter)
getwd()
setwd("../../../anti-sedentary-service")
numbers_only <- function(x) !grepl("\\D", x)
participants = c()
just_Added = c("10439","10198","10200","10270","10037","10063","10094","10211","10043","10218","10105","10086","10163")
for(f in list.files('data')){
  uid<-strsplit(strsplit(f,"_antised_data")[[1]],"user_")
  if (length(uid)==2){
    if (numbers_only(uid[[1]][[2]]) & nchar(uid[[1]][[2]])==5 & !(uid[[1]][[2]] %in% just_Added)){
      #& length(uid[[1]][[2]])==5
     
      participants<- c( participants,uid[[1]][[2]])
    }
  }

  
}
participants<- c( participants,"test-pedja")
participants
#"10006","10008","10027", "10032","10041","10055","10075","10110","10118","10137","10142","10157", "10187","10195","10199","10214","10217", "10271","10296","10307", "10327",  "10342",
#"10388", "10389","10399",
## GENERATE A FULL DATAFRAME OF ALL DATA ACROSS PARTICIPANTS
complete_data = matrix(nrow = 0, ncol = 15)
for (id in participants) {
  file_name = paste("data/user_", id, "_antised_data.csv", sep = "")
  #print(file_name)
  if(file.exists(file_name)) {
    data_for_participant = read.csv(file = file_name)
    #print(data_for_participant)
    complete_data = rbind(complete_data, data_for_participant)
  }
}
#rm("data_for_participant")

## CLEAN DATE TIME using lubridate package
library(lubridate)
complete_data$time = as_datetime(complete_data$time)
complete_data$unit = 1
## Number of POST requests from Nick's server, aggregated by user-day
numberrequests_results = aggregate(unit~day(time) + month(time) + userid, data = subset(complete_data, online_state != -1), FUN = sum)
## Number of interventions my microservice told Nick to send, aggregated by user-day
action_results = aggregate(action~day(time) + month(time) + userid, data = subset(complete_data, online_state != -1), FUN = sum)
## Number of times record individual in SEDENTARY STATE (state = 1) given by Nick's service, aggregated by user-day
state_results = aggregate(online_state~day(time) + month(time) + userid, data = subset(complete_data, online_state != -1), FUN = sum)
## Number of times of individual is AVAILABLE (availability = 1) given by Nick's service, aggregated by user-day
availability_results = aggregate(available~day(time) + month(time) + userid, data = subset(complete_data, online_state != -1), FUN = sum)

current_day_start = 30
current_block_start = 1
current_block_end = 7
current_month = 11


last_block_start = 24
last_block_end = 23

### NUMBER OF REQUESTS SUMMARIES
### BUILD BLOCKS: Jun 26th to Jul 2nd, Jul 3rd to Jul 10th, Jul 11th to Jul 13th, Jul 14th to 17th
#numberrequests_block1 = (numberrequests_results$`month(time)` == 7 & numberrequests_results$`day(time)` < 3 ) | (numberrequests_results$`month(time)` == 6 & numberrequests_results$`day(time)` >= 26)
##numberrequests_block2 = numberrequests_results$`month(time)` == 7 & (numberrequests_results$`day(time)` >= 3 & numberrequests_results$`day(time)` <= 10)
#numberrequests_block3 = numberrequests_results$`month(time)` == 7 & (numberrequests_results$`day(time)` >= 11 & numberrequests_results$`day(time)` <= 13)
#numberrequests_block4 = numberrequests_results$`month(time)` == 7 & (numberrequests_results$`day(time)` >= 14 & numberrequests_results$`day(time)` <= 17)
#numberrequests_block5 = numberrequests_results$`month(time)` == 7 & (numberrequests_results$`day(time)` >= 18 & numberrequests_results$`day(time)` <= 23)
#numberrequests_lastblock = numberrequests_results$`month(time)` == current_month & (numberrequests_results$`day(time)` >= last_block_start  & numberrequests_results$`day(time)` <= current_block_end)
numberrequests_currentblock = numberrequests_results$`month(time)` == current_month & (numberrequests_results$`day(time)` >= current_block_start  & numberrequests_results$`day(time)` <= current_block_end )
hist(numberrequests_results$unit[numberrequests_currentblock], main = paste("Per user-day July 31st-September12th ",current_block_start,"-",current_block_end), xlab = "Number of requests per day", breaks = 15)
#dev.off()
summary(numberrequests_results$unit[numberrequests_currentblock])




## GENERATE HISTOGRAMS FOR EACH TIMEWINDOW (i.e., each block)
# png(filename = "./figs/numrequest-Jul3-Jul10.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(numberrequests_results$unit[numberrequests_block1], main = "Per user-day from June 26th to July 2nd", xlab = "Number of requests per day", breaks = 15)
# dev.off()
#summary(numberrequests_results$unit[numberrequests_block1])
# png(filename = "./figs/numrequest-Jun26-Jul2.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(numberrequests_results$unit[numberrequests_block2], main = "Per user-day from July 3rd to July 10th", xlab = "Number of requests per day", breaks = 15)
# dev.off()
#summary(numberrequests_results$unit[numberrequests_block2])
# png(filename = "./figs/numrequest-Jul11-Jul13.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(numberrequests_results$unit[numberrequests_block3], main = "Per user-day from July 11th to July 13th", xlab = "Number of requests per day", breaks = 15)
# dev.off()
#summary(numberrequests_results$unit[numberrequests_block3])
# png(filename = "./figs/numrequest-Jul14-Jul17.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(numberrequests_results$unit[numberrequests_block4], main = "Per user-day from July 14th to July 17th", xlab = "Number of requests per day", breaks = 15)
# dev.off()
#summary(numberrequests_results$unit[numberrequests_block4])
#png(filename = "~/figs_heartsteps/numrequest-Jul18-Jul23.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(numberrequests_results$unit[numberrequests_block5], main = "Per user-day from July 18th to July 23rd", xlab = "Number of requests per day", breaks = 15)
#dev.off()
#summary(numberrequests_results$unit[numberrequests_block5])
#png(filename = "~/figs_heartsteps/numrequest-Jul24-Jul30.png", width = 480, height = 480, units = "px", pointsize = 12)


#dev.off()
#(numberrequests_results[numberrequests_block4,])[numberrequests_results$unit[numberrequests_block4] < 100,]


### NUMBER OF TIMES IN STATE == 1 (i.e., number of sedentary times)
#state_block1 = (state_results$`month(time)` == 7 & state_results$`day(time)` < 3 ) | (state_results$`month(time)` == 6 & state_results$`day(time)` >= 26)
#state_block2 = state_results$`month(time)` == 7 & (state_results$`day(time)` >= 3 & state_results$`day(time)` <= 10)
#state_block3 = state_results$`month(time)` == 7 & (state_results$`day(time)` >= 11 & state_results$`day(time)` <= 13)
#state_block4 = state_results$`month(time)` == 7 & (state_results$`day(time)` >= 14 & state_results$`day(time)` <= 17)
#state_block5 = state_results$`month(time)` == 7 & (state_results$`day(time)` >= 18 & state_results$`day(time)` <= 23)
#state_block6 = state_results$`month(time)` == 7 & (state_results$`day(time)` >= 22 & state_results$`day(time)` <= 24)
state_blockcurrent = state_results$`month(time)` == 10 & (state_results$`day(time)` >= current_block_start & state_results$`day(time)` <= current_block_end)
#hist(state_results$online_state[state_block1], main = "Per user-day from June 26th to July 2nd", xlab = "Number of available times per day", breaks = 15)
#summary(state_results$online_state[state_block1])
#hist(state_results$online_state[state_block2], main = "Per user-day from July 3rd to July 10th", xlab = "Number of available times per day", breaks = 15)
#summary(state_results$online_state[state_block2])
#hist(state_results$online_state[state_block3], main = "Per user-day from July 11th to July 13th", xlab = "Number of available times per day", breaks = 15)
#summary(state_results$online_state[state_block3])
#hist(state_results$online_state[state_block4], main = "Per user-day from July 14th to July 17th", xlab = "Number of available times per day", breaks = 15)
#summary(state_results$online_state[state_block4])

#hist(state_results$online_state[state_block5], main = "Per user-day from   July 18th to July 23rd", xlab = "Number of available times per day", breaks = 15)
#summary(state_results$online_state[state_block5])
hist(state_results$online_state[state_blockcurrent], main = paste("Per user-day July ",current_block_start,"-",current_block_end), xlab = "Number of available times per day", breaks = 15)
summary(state_results$online_state[state_blockcurrent])



### AVAILABILITY 
availability_block1 = (availability_results$`month(time)` == current_month & availability_results$`day(time)` < 3 ) | (availability_results$`month(time)` == 6 & availability_results$`day(time)` >= 26)
availability_block2 = availability_results$`month(time)` == current_month & (availability_results$`day(time)` >= 3 & availability_results$`day(time)` <= 10)
availability_block3 = availability_results$`month(time)` == current_month & (availability_results$`day(time)` >= 11 & availability_results$`day(time)` <= 13)
availability_block4 = availability_results$`month(time)` == 7 & (availability_results$`day(time)` >= 14 & availability_results$`day(time)` <= 17)
availability_block5 = availability_results$`month(time)` == 7 & (availability_results$`day(time)` >= 18 & availability_results$`day(time)` <= 23)
availability_blockcurrent = availability_results$`month(time)` == current_month & (availability_results$`day(time)` >= current_block_start & availability_results$`day(time)` <= current_block_end)


# png(filename = "./figs/available-Jul3-Jul10.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(availability_results$available[availability_block1], main = "Per user-day from June 26th to July 2nd", xlab = "Number of available times per day", breaks = 15)
# dev.off()
#summary(availability_results$available[availability_block1])
# png(filename = "./figs/available-Jun26-Jul2.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(availability_results$available[availability_block2], main = "Per user-day from July 3rd to July 10th", xlab = "Number of available times per day", breaks = 15)
# dev.off()
#summary(availability_results$available[availability_block2])
# png(filename = "./figs/available-Jun26-Jul2.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(availability_results$available[availability_block3], main = "Per user-day from July 11th to July 13th", xlab = "Number of available times per day", breaks = 15)
# dev.off()
#summary(availability_results$available[availability_block3])
# png(filename = "./figs/available-Jul13-Jul17.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(availability_results$available[availability_block4], main = "Per user-day from July 14th to July 17th", xlab = "Number of available times per day", breaks = 15)
# dev.off()
#summary(availability_results$available[availability_block4])
# dev.off()
#png(filename = "~/figs_heartsteps/available-Jul18-Jul23.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(availability_results$available[availability_block5], main = "Per user-day from July 18th to July 23rd", xlab = "Number of available times per day", breaks = 15)
#dev.off()
#summary(availability_results$available[availability_block5])

png(filename = "~/figs_heartsteps/available-Jul31-Sep12.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(availability_results$available[availability_blockcurrent], main = paste("Per user-day from July ", current_block_start,"-",current_block_end), xlab = "Number of available times per day", breaks = 15)
dev.off()
summary(availability_results$available[availability_blockcurrent])## FRACTION


#hist(availability_results$available[availability_block1]/numberrequests_results$unit[numberrequests_block1], main = "Per user-day from June 26th to July 2nd", xlab = "Fraction of request times the user is available per day", breaks = 15)
#hist(availability_results$available[availability_block2]/numberrequests_results$unit[numberrequests_block2], main = "Per user-day from July 3rd to July 10th", xlab = "Fraction of request times the user is available per day", breaks = 15)
#hist(availability_results$available[availability_block3]/numberrequests_results$unit[numberrequests_block3], main = "Per user-day from July 11rd to July 13th", xlab = "Fraction of request times the user is available per day", breaks = 15)
#hist(availability_results$available[availability_block4]/numberrequests_results$unit[numberrequests_block4], main = "Per user-day from July 14rd to July 17th", xlab = "Fraction of request times the user is available per day", breaks = 15)
#hist(availability_results$available[availability_block5]/numberrequests_results$unit[numberrequests_block5], main = "Per user-day from July 18th to July 23rd", xlab = "Fraction of request times the user is available per day", breaks = 15)

### ACTIONS
block5_title = "Per user-day from July 18th to July 23rd"
#action_block1 = (action_results$`month(time)` == 7 & action_results$`day(time)` < 3 ) | (action_results$`month(time)` == 6 & action_results$`day(time)` >= 26)
#action_block2 = action_results$`month(time)` == 7 & (action_results$`day(time)` >= 3 & action_results$`day(time)` <=10)
#action_block3 = action_results$`month(time)` == 7 & (action_results$`day(time)` >= 11 & action_results$`day(time)` <=13)
#action_block4 = action_results$`month(time)` == 7 & (action_results$`day(time)` >= 14 & action_results$`day(time)` <=17)
#action_block5 = action_results$`month(time)` == 7 & (action_results$`day(time)` >= 18 & action_results$`day(time)` <=23)
#png(filename = "~/figs_heartsteps/actions-Jul18-Jul23.png", width = 480, height = 480, units = "px", pointsize = 12)
#hist(action_results$action[action_block4], main = paste(block4_title), xlab = "Number of anti-sedentary messages per day", breaks = 15)
#hist(action_results$action[action_block5], main = paste(block5_title), xlab = "Number of anti-sedentary messages per day", breaks = 15)
# dev.off()
#summary(action_results$action[action_block5])
action_blockcurrent = action_results$`month(time)` == current_month & (action_results$`day(time)` >= current_block_start & action_results$`day(time)` <=current_block_end) | (action_results$`month(time)` == 7 & (action_results$`day(time)` == 31 ) | action_results$`month(time)` == 8)
png(filename = "~/figs_heartsteps/actions-Jul31-Sep12.png", width = 480, height = 480, units = "px", pointsize = 12)

hist(action_results$action[action_blockcurrent], main = paste( "Per user-day July-31st-September 12th "), xlab = "Number of anti-sedentary messages per day", breaks = 15)
dev.off()
summary(action_results$action[action_blockcurrent])
x=aggregate(action ~ userid, subset(action_results, action_blockcurrent ), FUN = mean,drop=FALSE)
print(x,digits=3)


