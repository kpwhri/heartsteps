## Nightly Data Download Overview
This feature is currently disabled, but when running it will export de-identified participant data to a google storage bucket after the participant's nightly update script runs.

Files are exported per participant, and are described individually below. In the exported data, each participant's heartsteps_id is used to prefix the file name.

### fitibit_minutes.csv
This file is a record of minute level data that is gathered from the Fitbit API. This data is often accumulated and used in different tables.

* **Username** the heartsteps id of the participant
* **Fitbit Account** is the Fitbit Account ID for the participant
* **Timezone** is the timezone for the date.
* **Date** is the date the row corresponds to. This is formated as `YYYY-MM-DD`
* **Time** is the time that the row corresponds to. This is formatted using 24-hour time, and is `HH:MM:SS`
* **Steps** is the number of steps reported by Fitbit in the minute that the row represents. It's possible for this value to be Null, which means the HeartSteps server didn't get any values from the Fitbit API for this minute.
* **Heart Rate** is the minute level heart rate report by Fitbit for the minute the row represents. It's possible for this value to be Null, which means the HeartSteps server didn't recieve values from the Fitbit API for this minute.

### adherence_metrics.csv
This is an export of participant behavior at a daily grainularity. 

### anti_sedentary_decisions.csv
This is an export of every anti-sedentary decision recorded for each participant.

### anti_sedentary_service_requests.csv
This is an export of requests sent to and received from the anti-sedentary service.

### walking_suggestion_decision.csv
This is an export of every walking suggestion decision recorded for each participant.

### walking_suggestion_service_requests.csv
This is an export of requests sent to and reveived from the walking suggestion service.
