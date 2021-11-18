# src / pages / baseline-week

## Purpose
This module holds participants from the intervention during the baseline period. The baseline period is fetched from the server (participant.models.Study) via ParticipantService

## Description

* baseline-week.gaurd.ts
  - It filters out unauthorized requests to welcome page.
    
* baseline-week.module.ts
  - It describes what modules and classes are used, or defined in this module.

* baseline-week.page.html
  - It describes how page should look like.
    1. a title
    2. a description about what the "baseline" is.
    3. a specific guidelines for the baseline. It brings {{baselinePeriod}} argument from **ParticipantInformationService**, which loads up from the server's **participant.models.Study** model. 8-hours-per-day is fixed value. (why?)
    4. the number of days worn Fitbit
      - in the form of **text** and **bubbles**.
    5. today's activity summary (steps, miles, earned minutes)
      - which includes the **Reload Data** button and the **last update time**.
    6. **study staff contact information**
    7. **settings** button
  - It receives data from ***baseline-week.page.ts***.

* baseline-week.page.ts
  - It defines 
    1. **Day** class: for the day bubble display
    2. **BaselineWeekPage** class: to provide data and logic to ***baseline-week.page.html***. It includes
        1. **member variables**: summary, days, numberDaysWorn, baselinePeriod, studyContactName, studyContactPhone
        2. **constructor**: subscribe to activity summary and study contact info.
        3. **reload()**: refreshes daily summary and all the follow-ups
        4. **dateToDay()**: convert wornDay data into bubble **Day**.
        5. **setBaselinePeriod()**: brings the length of baseline period from server (participantService)
        6. **setDays()**: fill up all data for previous baseline period.
        7. **format functions**: formats date into string
        8. **goToSettings()**: redirects to settings page

* baseline-week.scss
