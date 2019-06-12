#! /usr/bin/Rscript
library('rjson')

# script is assuming JSON output always
args <- commandArgs(trailingOnly = TRUE)
input = fromJSON(args[1])

## Required packages and source files
source("functions.R")

# payload = ' {
#   "userid": [ 2 ],
#   "decisionid": [ 1803312 ] ,
#   "time": [ "2018-10-12 10:00" ] ,
#   "daystart": [ "2018-10-12 20:00" ] ,
#   "dayend": [ "2018-10-12 8:00" ] ,
#   "state": [ 0 ] ,
#   "steps": [ 0 ] ,
#   "available": [ 0 ]
# }
# '
# input = fromJSON(payload)

# If userID file exists then pull that in
# Otherwise construct a dataframe
setwd("./data/")
file_name = paste("user_",input$userid,"_antised_data.csv", sep = "")

if(file.exists(file_name)) {
  user.data = read.csv(file = file_name, header= TRUE)
} else {
  user.data = data.frame(userid = input$userid, decisionid = input$decisionid,
                         time = input$time, daystart = input$dayStart, dayend = input$dayEnd,
                         probaction = 0.0, action = 0.0, missingindicator = 0, duplicate = FALSE)
}

if( any(is.na(strptime(user.data$time, "%Y-%m-%d %H:%M"))) ) {
  user.data$time = as.POSIXct(strptime(user.data$time, "%m/%d/%y %H:%M"), tz = "Etc/GMT+6")
  user.data$daystart = as.POSIXct(strptime(user.data$daystart, "%m/%d/%y %H:%M"), tz = "Etc/GMT+6")
  user.data$dayend = as.POSIXct(strptime(user.data$dayend, "%m/%d/%y %H:%M"), tz = "Etc/GMT+6")
} else {
  user.data$time = as.POSIXct(strptime(user.data$time, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
  user.data$daystart = as.POSIXct(strptime(user.data$daystart, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
  user.data$dayend = as.POSIXct(strptime(user.data$dayend, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
}

current.time = as.POSIXct(strptime(input$time, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")

if ( any(is.element(user.data$time,current.time)) ) {
    ## IF ROW ALREADY EXISTED THEN ADD INFO TO THE ROW
    obs.row = which(is.element(user.data$time,current.time))
    user.data$batch_state[obs.row] = input$state
    user.data$batch_step[obs.row] = input$steps
    results <- list(append = FALSE)
    write.csv(user.data, file = file_name, row.names = FALSE)
} else {
  ## IF ROW DID NOT EXIST THEN APPEND ROW
  current.time = as.POSIXct(strptime(input$time, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
  final.time = as.POSIXct(strptime(input$dayend, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
  beginning.time = as.POSIXct(strptime(input$daystart, "%Y-%m-%d %H:%M"), tz = "Etc/GMT+6")
  
  temp.data = data.frame(userid = input$userid, decisionid = input$decisionid,
                         time = current.time, daystart =beginning.time, dayend = final.time,
                         online_state = -1, online_step = -1, available = 0,
                         batch_state = input$state, batch_step = input$steps, probaction = 0.0, action = 0.0,
                         missingindicator = 1, duplicate = FALSE)
  results <- list(append = TRUE)
  write.csv(rbind(user.data, temp.data), file = file_name, row.names = FALSE)
}

# output the results
cat(toJSON(results))
