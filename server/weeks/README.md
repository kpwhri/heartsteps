This weeks app enables the weekly survey that is sent to HeartSteps participants.
A weekly survey has 4 sections; weekly barriers, weekly goal, weekly questions, and next week's plans.

For each participant week, start and end dates don't overlap.
Weeks start on a Monday and end on a Sunday.
Each week is numbered numerically, starting with 1.

A weekly reflection message is sent to participants that reminds participants to complete the weekly survey.
The weekly reflection message time is set in the weekly_reflection app. By default the weekly reflection time is Sunday at 7pm on the participant's current timezone.

## Weekly Barriers
Each week, a study participant picks the barriers they had to being active during that week, then states if they barriers will continue.
Participants are able to add their own options to this list.

The week model saves the list of barrier options that were presented to the participant as a JSON.
The barriers that a participant selects is saved as a WeeklyBarrier that is associated to the week.
There are properties on the week model that return [weekly barrier options](https://github.com/kpwhri/heartsteps/blob/master/server/weeks/models.py#L168-L171) and [weekly barriers selected](https://github.com/kpwhri/heartsteps/blob/master/server/weeks/models.py#L133-L139) as a list of strings.

## Weekly Goals
Each participant's goal for that week is saved as a number of minutes, and the participant's confidence is saved as a float, but is created by a 5 item likert scale with values from "not at all" to "very much".

A participant first sets their weekly goal during the previous week's weekly survey. A participant can change their weekly goal in the settings page of the HeartSteps app. Changes to the weekly goal are not currently tracked (crap), but page view logs could be checked to determine if the participant changed their weekly goal.

There is a default goal initially set for each participant. The default value for a weekly goal is the previous weeks goal plus 20 minutes. If there is no default goal, the minimum default goal value is used. The minimum value of the default goal is 90 minutes and the maximum value is 150 minutes. 

The goal entered by a participant can be zero and any positive integer. The client app adjusts goals in 5 minute increments.

## Weekly Questions
This is a survey that is shown to participants weekly. These surveys extend the generic Survey model and use WeekQuestions.
The weekly surveys are not required, so there might be null values.

## Weekly Plans
Plans created during the weekly planning process are not specifically saved. To determine if a plan was created during the weekly planning process you should look at the page views.
