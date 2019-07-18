## DRAG IN ALL DATA FOR PEOPLE 
## MANUAL LIST OF TEST PARTICIPANTS
## Numbers = "REAL PEOPLE"
## "Test-XXXX" = "FAKE PERSON" (e.g., peng, walter)
setwd("~/Documents/github/heartsteps/anti-sedentary-service/data/")
participants = c("10008", "10032", "10187", "10296", "10214", 
                 "10296", "10388", "10399",
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
# probability_results = aggregate(probaction~day(time) + month(time) + userid, data = subset(complete_data, available == 1), FUN = sum)


### NUMBER OF REQUESTS 
numberrequests_block1 = numberrequests_results$`month(time)` == 7 & (numberrequests_results$`day(time)` >= 3 & numberrequests_results$`day(time)` <= 10)
numberrequests_block2 = (numberrequests_results$`month(time)` == 7 & numberrequests_results$`day(time)` < 3 ) | (numberrequests_results$`month(time)` == 6 & numberrequests_results$`day(time)` >= 26)
# png(filename = "./figs/numrequest-Jul3-Jul10.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(numberrequests_results$unit[numberrequests_block1], main = "Per user-day from July 3rd to July 7th", xlab = "Number of requests per day", breaks = 15)
# dev.off()
summary(numberrequests_results$unit[numberrequests_block1])
# png(filename = "./figs/numrequest-Jun26-Jul2.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(numberrequests_results$unit[numberrequests_block2], main = "Per user-day from June 26th to July 2nd", xlab = "Number of requests per day", breaks = 15)
# dev.off()
summary(numberrequests_results$unit[numberrequests_block2])

### NUMBER OF TIMES IN STATE == 1
state_block1 = state_results$`month(time)` == 7 & (state_results$`day(time)` >= 3 & state_results$`day(time)` <= 10)
state_block2 = (state_results$`month(time)` == 7 & state_results$`day(time)` < 3 ) | (state_results$`month(time)` == 6 & state_results$`day(time)` >= 26)
hist(state_results$online_state[state_block1], main = "Per user-day from July 3rd to July 7th", xlab = "Number of available times per day", breaks = 15)
summary(state_results$online_state[state_block1])
hist(state_results$online_state[state_block2], main = "Per user-day from June 26th to July 2nd", xlab = "Number of available times per day", breaks = 15)
summary(state_results$online_state[state_block2])

### AVAILABILITY 
availability_block1 = availability_results$`month(time)` == 7 & (availability_results$`day(time)` >= 3 & availability_results$`day(time)` <= 10)
availability_block2 = (availability_results$`month(time)` == 7 & availability_results$`day(time)` < 3 ) | (availability_results$`month(time)` == 6 & availability_results$`day(time)` >= 26)
# png(filename = "./figs/available-Jul3-Jul10.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(availability_results$available[availability_block1], main = "Per user-day from July 3rd to July 7th", xlab = "Number of available times per day", breaks = 15)
# dev.off()
summary(availability_results$available[availability_block1])
# png(filename = "./figs/available-Jun26-Jul2.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(availability_results$available[availability_block2], main = "Per user-day from June 26th to July 2nd", xlab = "Number of available times per day", breaks = 15)
# dev.off()
summary(availability_results$available[availability_block2])

## FRACTION
hist(availability_results$available[availability_block1]/numberrequests_results$unit[numberrequests_block1], main = "Per user-day from July 3rd to July 7th", xlab = "Fraction of request times that the user is sedentary per day", breaks = 15)
hist(availability_results$available[availability_block2]/numberrequests_results$unit[numberrequests_block2], main = "Per user-day from June 26th to July 2nd", xlab = "Number of available times per day", breaks = 15)

hist(availability_results$available[availability_block1]/state_results$online_state[state_block1], main = "Per user-day from July 3rd to July 7th", xlab = "Fraction of sedentary times that the user is available per day", breaks = 15)
hist(availability_results$available[availability_block2]/state_results$online_state[numberrequests_block2], main = "Per user-day from June 26th to July 2nd", xlab = "Fraction of sedentary times that the user is available per day", breaks = 15)

### ACTIONS
action_block1 = action_results$`month(time)` == 7 & (action_results$`day(time)` >= 3 & action_results$`day(time)` <=10)
action_block2 = (action_results$`month(time)` == 7 & action_results$`day(time)` < 3 ) | (action_results$`month(time)` == 6 & action_results$`day(time)` >= 26)
png(filename = "./figs/actions-Jul3-Jul10.png", width = 480, height = 480, units = "px", pointsize = 12)
hist(action_results$action[action_block1], main = "Per user-day from July 3rd to July 7th", xlab = "Number of anti-sedentary messages per day", breaks = 15)
dev.off()
# hist(action_results$action[action_block2], main = "Per user-day from June 26th to July 2nd", xlab = "Number of anti-sedentary messages per day")
aggregate(action ~ userid, subset(action_results, `day(time)` >=3 & `month(time)` == 7), FUN = mean)
# aggregate(action ~ userid, subset(action_results, (`day(time)` < 2 & `month(time)` == 7) | (`day(time)` >= 26 & `month(time)` == 6)), FUN = mean)
          