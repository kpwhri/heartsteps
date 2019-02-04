# Walking Suggestion Service
The walking suggestion service suggests if the heartsteps-server should send a walking-suggestion message to the participant.

## Installation and runtime
To run the walking-suggestion-service, the heartsteps_service-template image needs to be built first. The following commands will build the heartsteps_service-template and then run the walking-suggestion-service.

``` bash
docker-compose build service-template
docker-compose run --service-ports walking-suggestion-service
```

## 1. Initialization

### WHEN TO CALL

The *initialize* service is called for each participant at the end of the warm up period (assuming to be 7 days; during this period, the participant only has the fitbit but the HS app is not installed). Note that it needs to be called (at least) after the participant has specified the five time slots so that we can retrieve the pre- and post-30 minutes step count around each time slot.



### INPUT-OUTPUT
The *initialize* service has no output except for a message indicating successful initializaiton.  Below is an example of json input. 

~~~json
{
	"userID":1,
	"totalStepsArray":[12310,10000,null,10000,10000,11111,22222],
	"preStepsMatrix":[
		{"steps":[null,2,null,30,10]},
		{"steps":[123,243,1231,30,100]},
		{"steps":[103,1232,null,301,103]},
		{"steps":[100,2,null,30,null]},
		{"steps":[1100,23,null,303,100]},
		{"steps":[100,2,null,30,100]},
		{"steps":[100,2,null,30,100]}],
	"postStepsMatrix":[
		{"steps":[100,2,null,30,100]},
		{"steps":[100,2,null,3012,100]},
		{"steps":[null,21,null,330,1010]},
		{"steps":[null,2,0,30,null]},
		{"steps":[100,2,1,30,100]},
		{"steps":[100,2,15,30,100]},
		{"steps":[100,2,null,30,100]}]
}
~~~

1. `userID`: the user ID.

3. `totalStepsArray` 

	- A vector of the 7-day total steps that are tracked by Fitbit for each of the warm up days. Fitbit defines a day as the period from 12:00am to 11:59pm in the participant's local time. The data reported here will be directly collected from the [Fitbit API's daily activity summary](https://dev.fitbit.com/build/reference/web-api/activity/#get-daily-activity-summary). The vector is ordered in chronological order, e.g. the first one corresponds to the total numbers of steps in the first day.
	- When any of these numbers are missing, it will be assumed that it is a programming error and set to `null`.  Any days where the participant doesn't wear the device (meaning doesn't register any steps, and doesn't have a heart rate) will be marked as `null` rather than zero steps.

	
6. `preStepsMatrix` and `postStepsMatrix`
	- `preStepsMatrix` is a 7 by 5 matrix of step counts collected 30 min prior to each of five decision times during the 7-day warm up period. The first element corresponds to the five pre-treatment step counts (in chronological order) in the first day and so on.  `postStepsMatrix` is for the step count 30 min after each decision time. 
	- Step counts could be missing because the participant isn't wearing their Fitbit or the data is unable to be queried. If any of these step count are missing `null` will be used instead of an actual number. Missing is not same as a step count of zero.


### CONDITION CHECKING

The current version of *initialize* service requires the input satisifying the following conditions (otherwise, an error message will pop up and the bandit service will break)

1. Include all the required infomation (e.g. user id, total steps array, pre and post steps matrix)
1. Inlcude all 7-day data for the totol step count (some of them are allowed to be missing) and all 7-day of pre and post step counts for each decision time (can be missing)
2. At least one observation for the total step and pre and post step count at each decision time (e.g. does not allow the case where all of the pre-30 min step at the first decision time are missing)




## 2. Decision Making

### WHEN TO CALL
The *decision* service is called for each pariticipant at each of the decision times during the study (does not include the warm-up period). It *must* be called at each of five decision times in a day (even if the participant is currently unavailable). *(It is possible that a technical server failure would stop the decision service from being called, but we hope to avoid that situation)*


### INPUT-OUT
The *decision* service outputs a json file including `probability`, the randomization probability and `send`, the indicator of whether to send the activity message. Below is an example of the output.

~~~json
{
    "probability": 0.5,
    "send": true
}
~~~

Shown below is an example of json input for user `1` at decision time `2` on day `3`. 

~~~json
{
  	"userID": 1,
 	 "studyDay": 3,
 	 "decisionTime": 2,
 	 "availability": true,
 	 "priorAnti": false,
 	 "lastActivity": false,
 	 "location": 1
}
~~~

1. `userID`: the user ID. 

2. `studyDay`: index of the current day since the begining of the study, starting at `1` on the first day. 

3. `decisionTime`: index of the current time slot (i.e. decision time) in a day, ranging from `1` to `5`

4. `availability`: the indicator of availability at the current decision time (either `true` or `false`)

5. `priorAnti`

	- For the 1st decision time, `priorAnti` is the indicator of whether there is any anti-sedentary message delivered to user's phone between the "start of the day" and the 1st decision time. The "start of day" here is specified in the anti-sedentary message scheduling. If a participant sets their first decision time to before the anti-sedentary services' "start of day" this will always return false.
	- For rest of the decision times (2nd to 5th), say decision time $t$, `priorAnti` is the indicator of whether there is any anti-sedentary message delivered to user's phone between the decision time $(t-1)$ to the current decision time $t$. 
	- Can either be `true` or `false`

6. `lastActivity`

	- For the 2nd to 5th decision time, say decision time $t$, `lastActivity` is the indicator of whether the activity message is delivered to user's phone at the previous decision time (e.g. decision time $(t-1)$)
	- For the 1st decision time, `lastActivity` is set to `false` (this is not used)
	- Can either be `true` or `false`

7. `location`
	- The calssicaiton of user's current location: `2` if currently at home, `1` if currently  at work, `0` otherwise.
	- If the current location is unknown, set to `0`. 


### CONDITION CHECKING

The current version of *decision* service requires the input satisifying the following conditions (otherwise, an error message will pop up and the bandit service will break)

1. The *decision* service does not skip any previous decision times (e.g. the decision service is required to call 5 times per day since the begining of the study). This is done by examing the input `studyDay` and `decisionTime`. 
2. All the required information is included in the input
2. The type of each variable is consistent with the above description (e.g. `location` can only be `0`, `1` or `2`,  `availability` can only be `true` or `false` and so on.)
3. There is no missing data in the input. 



## 3. Nightly Update

### WHEN TO CALL
The *nightly* service is called at every night after the 5th decision time during the study (does not include the warm up period). The exact time at which the *nightly* service is called needs to satisfy: 

- after we know all the required information (e.g. the app click data and the total steps, depending on the exact definition)
- after the end of the day specified in the anti-sedentary message secheduling. That is, there cannot be any anti-sedentary message sent after the *nightly* service is called. 

### INPUT-OUTPUT
The *nightly* service has no output except for a message indicating successful update.  Below is an exmaple of json input for user `1` finishing day `2`. 

~~~json
{
	"userID":1,
	"studyDay":2,
	"priorAnti":false,
	"lastActivity":false,
	"temperatureArray":[30,33.4,8.5,23.9,38.1],
	"appClick":503,
	"totalSteps":6584,
	"preStepsArray":[12,50,100,0,null],
	"postStepsArray":[300,null,100,130,31]
}
~~~

1. `userID`: the user ID. 

2. `studyDay`: index of the current day since the begining of the study, starting at `1` on the first day. 

3. `priorAnti`: the indicator of whether there is any anti-sedentary message delivered to user's phone between the 5th decision time and the "end of the day" specified in the anti-sedentary message scheduling.  Can either be `true` or `false`. If the participant sets their 5th decision time to a period after the anti-sedentary service's "end of day" then `priorAnti` will be set to `false`

4. `lastActivity`: the indicator of whether the activity message is delivered to user's phone at the 5th decision time in the current day.  Can either be `true` or `false`

5. `temperatureArray`: 
	- A vector of the temperatures (in Celsius degree) at each of the five locations during the day.
	- If any of the temperatures is unknown, then the average temperature of all the participant's registered places (home and work) will be substuted for the actual temperature.

6. `appClick`

	- The number of app screens encountered in the current day from 12:00 am to 11:59 pm. 
	- When any of these numbers are missing it will be assumed this is a programming error and set to `null`. If there is a day with no interaction from a participant, then the reported clicks for the day will be zero.

7. `totalSteps`

	- Total of steps that are tracked by Fitbit the specific day. Fitbit defines a day as the period from 12:00am to 11:59pm in the participant's local time. The data reported here will be directly collected from the [Fitbit API's daily activity summary](https://dev.fitbit.com/build/reference/web-api/activity/#get-daily-activity-summary).
	-  Any missing data will be assumed that it is a programming error. and will set to `null`. Any days where the participant doesn't wear the device (meaning doesn't register any steps, and doesn't have a heart rate) will be marked as null rather than zero steps. 

8. `preStepsArray` and `postStepsArray`

	- `preStepsArray ` is a vector of step counts collected 30 min prior to each of five decision times in the current day. It is in chronological order, e.g. the first element corresponds to the 30 min pre-treatment step counts at the first decision time and so on.  
	- `postStepsMatrix` is for the step count 30 min after each decision time. 
	- If any of these step count are missing, it will be considered a programming error, and `null` will be used. This data will be pulled from the [Fitbit API's intra-day step count](https://dev.fitbit.com/build/reference/web-api/activity/#get-activity-intraday-time-series). Here missing is not same as no step count which should be 0 in the input.


### CONDITION CHECKING

The current version of *nightly* service requires the input satisifying the following conditions (otherwise, an error message will pop up and the bandit service will break)

1. All the required information is included in the input
2. There are five records in the input `temperatureArray`, `preStepsArray`, `postStepsArray` (including the missing ones)
4. The type of data is consistent with the above desciption 
5. The *nighty* service is called after the 5th decision time in the current day (e.g. the *decision* service has been called 5 times)







