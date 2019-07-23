## DRAG IN ALL DATA FOR PEOPLE 
## MANUAL LIST OF TEST PARTICIPANTS
## Numbers = "REAL PEOPLE"
## "Test-XXXX" = "FAKE PERSON" (e.g., peng, walter)
setwd("~/Documents/github/heartsteps/anti-sedentary-service/data/")
participants = c("10008", "10032", "10187", "10296", "10214", 
                 "10388", "10399",
                 "test-donna", "test-nickreid", "test-pedja", 
                 "test-mash", "test-peng")
## GENERATE A FULL DATAFRAME OF ALL DATA ACROSS PARTICIPANTS
complete_data = matrix(nrow = 0, ncol = 14)
for (id in participants) {
  file_name = paste("user_", id, "_antised_data.csv", sep = "")
  if(file.exists(file_name)) {
    data_for_participant = read.csv(file = file_name)
    complete_data = rbind(complete_data, data_for_participant)
  }
}
rm("data_for_participant")

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

### NUMBER OF REQUESTS SUMMARIES
### BUILD BLOCKS: Jun 26th to Jul 2nd, Jul 3rd to Jul 10th, Jul 11th to Jul 13th, Jul 14th to 17th
numberrequests_block1 = (numberrequests_results$`month(time)` == 7 & numberrequests_results$`day(time)` < 3 ) | (numberrequests_results$`month(time)` == 6 & numberrequests_results$`day(time)` >= 26)
numberrequests_block2 = numberrequests_results$`month(time)` == 7 & (numberrequests_results$`day(time)` >= 3 & numberrequests_results$`day(time)` <= 10)
numberrequests_block3 = numberrequests_results$`month(time)` == 7 & (numberrequests_results$`day(time)` >= 11 & numberrequests_results$`day(time)` <= 13)
numberrequests_block4 = numberrequests_results$`month(time)` == 7 & (numberrequests_results$`day(time)` >= 14 & numberrequests_results$`day(time)` <= 17)

## GENERATE HISTOGRAMS FOR EACH TIMEWINDOW (i.e., each block)
# png(filename = "./figs/numrequest-Jul3-Jul10.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(numberrequests_results$unit[numberrequests_block1], main = "Per user-day from June 26th to July 2nd", xlab = "Number of requests per day", breaks = 15)
# dev.off()
summary(numberrequests_results$unit[numberrequests_block1])
# png(filename = "./figs/numrequest-Jun26-Jul2.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(numberrequests_results$unit[numberrequests_block2], main = "Per user-day from July 3rd to July 10th", xlab = "Number of requests per day", breaks = 15)
# dev.off()
summary(numberrequests_results$unit[numberrequests_block2])
# png(filename = "./figs/numrequest-Jul11-Jul13.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(numberrequests_results$unit[numberrequests_block3], main = "Per user-day from July 11th to July 13th", xlab = "Number of requests per day", breaks = 15)
# dev.off()
summary(numberrequests_results$unit[numberrequests_block3])
# png(filename = "./figs/numrequest-Jul14-Jul17.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(numberrequests_results$unit[numberrequests_block4], main = "Per user-day from July 14th to July 17th", xlab = "Number of requests per day", breaks = 15)
# dev.off()
summary(numberrequests_results$unit[numberrequests_block4])

(numberrequests_results[numberrequests_block4,])[numberrequests_results$unit[numberrequests_block4] < 100,]


### NUMBER OF TIMES IN STATE == 1 (i.e., number of sedentary times)
state_block1 = (state_results$`month(time)` == 7 & state_results$`day(time)` < 3 ) | (state_results$`month(time)` == 6 & state_results$`day(time)` >= 26)
state_block2 = state_results$`month(time)` == 7 & (state_results$`day(time)` >= 3 & state_results$`day(time)` <= 10)
state_block3 = state_results$`month(time)` == 7 & (state_results$`day(time)` >= 11 & state_results$`day(time)` <= 13)
state_block4 = state_results$`month(time)` == 7 & (state_results$`day(time)` >= 14 & state_results$`day(time)` <= 17)
hist(state_results$online_state[state_block1], main = "Per user-day from June 26th to July 2nd", xlab = "Number of available times per day", breaks = 15)
summary(state_results$online_state[state_block1])
hist(state_results$online_state[state_block2], main = "Per user-day from July 3rd to July 10th", xlab = "Number of available times per day", breaks = 15)
summary(state_results$online_state[state_block2])
hist(state_results$online_state[state_block3], main = "Per user-day from July 11th to July 13th", xlab = "Number of available times per day", breaks = 15)
summary(state_results$online_state[state_block3])
hist(state_results$online_state[state_block4], main = "Per user-day from July 14th to July 17th", xlab = "Number of available times per day", breaks = 15)
summary(state_results$online_state[state_block4])


### AVAILABILITY 
availability_block1 = (availability_results$`month(time)` == 7 & availability_results$`day(time)` < 3 ) | (availability_results$`month(time)` == 6 & availability_results$`day(time)` >= 26)
availability_block2 = availability_results$`month(time)` == 7 & (availability_results$`day(time)` >= 3 & availability_results$`day(time)` <= 10)
availability_block3 = availability_results$`month(time)` == 7 & (availability_results$`day(time)` >= 11 & availability_results$`day(time)` <= 13)
availability_block4 = availability_results$`month(time)` == 7 & (availability_results$`day(time)` >= 14 & availability_results$`day(time)` <= 17)

# png(filename = "./figs/available-Jul3-Jul10.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(availability_results$available[availability_block1], main = "Per user-day from June 26th to July 2nd", xlab = "Number of available times per day", breaks = 15)
# dev.off()
summary(availability_results$available[availability_block1])
# png(filename = "./figs/available-Jun26-Jul2.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(availability_results$available[availability_block2], main = "Per user-day from July 3rd to July 10th", xlab = "Number of available times per day", breaks = 15)
# dev.off()
summary(availability_results$available[availability_block2])
# png(filename = "./figs/available-Jun26-Jul2.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(availability_results$available[availability_block3], main = "Per user-day from July 11th to July 13th", xlab = "Number of available times per day", breaks = 15)
# dev.off()
summary(availability_results$available[availability_block3])
# png(filename = "./figs/available-Jul13-Jul17.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(availability_results$available[availability_block4], main = "Per user-day from July 14th to July 17th", xlab = "Number of available times per day", breaks = 15)
# dev.off()
summary(availability_results$available[availability_block4])


## FRACTION
hist(availability_results$available[availability_block1]/numberrequests_results$unit[numberrequests_block1], main = "Per user-day from June 26th to July 2nd", xlab = "Fraction of request times the user is available per day", breaks = 15)
hist(availability_results$available[availability_block2]/numberrequests_results$unit[numberrequests_block2], main = "Per user-day from July 3rd to July 10th", xlab = "Fraction of request times the user is available per day", breaks = 15)
hist(availability_results$available[availability_block3]/numberrequests_results$unit[numberrequests_block3], main = "Per user-day from July 11rd to July 13th", xlab = "Fraction of request times the user is available per day", breaks = 15)
hist(availability_results$available[availability_block4]/numberrequests_results$unit[numberrequests_block4], main = "Per user-day from July 14rd to July 17th", xlab = "Fraction of request times the user is available per day", breaks = 15)

### ACTIONS
block4_title = "Per user-day from July 14th to July 17th"
action_block1 = (action_results$`month(time)` == 7 & action_results$`day(time)` < 3 ) | (action_results$`month(time)` == 6 & action_results$`day(time)` >= 26)
action_block2 = action_results$`month(time)` == 7 & (action_results$`day(time)` >= 3 & action_results$`day(time)` <=10)
action_block3 = action_results$`month(time)` == 7 & (action_results$`day(time)` >= 11 & action_results$`day(time)` <=13)
action_block4 = action_results$`month(time)` == 7 & (action_results$`day(time)` >= 14 & action_results$`day(time)` <=17)
# png(filename = "./figs/actions-Jul14-Jul17.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(action_results$action[action_block4], main = paste(block4_title), xlab = "Number of anti-sedentary messages per day", breaks = 15)
# dev.off()
summary(action_results$action[action_block4])
aggregate(action ~ userid, subset(action_results, action_block4), FUN = mean)
