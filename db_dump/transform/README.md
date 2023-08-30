# Transform App

This app is a python code created to organize the database dump generated after the end of the JustWalk JITAI study and upload it to the HDH MongoDB server. It was created with repeated execution in mind, so you don't have to worry about the data getting tangled even if you run it repeatedly, but you can set flags for each step to reduce the time required. (Useful in the development process)

## 1. Structure of the dump files

The dump files follow the database tables of the originally configured heartsteps app. We've created a csv file for each table (see load_csv app under the db_dump directory) and assume that these csv files are loaded into a locally running temporary mongodb (run with docker compose), so if you have a MongoDB instance floating around from another development project, it may misbehave.


## 2. Architecture of the Transform app

### transform_participants
This function transforms all the information related to the participant. It fills up the participants collection in the database. The following substeps occur:

- `participant` collection in the target database is deleted.
- `participants_study`, `participants_cohort` collections in the source database are used to identify `study_id` and `cohort_id`.
- `cohort_id` is used to select the actual participants only.
- picking up `heartsteps_id`, `user_id`, `birth_year`, `study_start_date` columns only.
- participant list is inserted into the target database.

### transform_daily
This function transforms the basic information from multiple collections in the source database and prepare for the base to fill up the additional "daily" information. The following substeps occur:

- `daily` collection in the target database is deleted.
- for the participants in the `participant` collection, "level" information from the source database is gathered. It is used to create a `daily` dataframe.
- append `day_index` (integer value, days elapsed since the start of the study) column to `daily` dataframe
- fill out missing dates' levels with RE (resting = no intervention) for the first 10 days and trailing dates
- append `step_goal` column
- fill out missing dates' goals with 2000.

### transform_minute_step, transform_minute_heart_rate
These two functions simply load the data from source database and import them to the target database. Since the data sizes are too big, `ray` is used.

### copy_daily_steps_and_heart_rate
This step aggregates the daily steps and heart rates and update the `daily` collection.

### transform_survey
This step loads up the survey, message, messagereceipt, pageview tables to organize the notifications and surveys for the following steps. The result collection is `survey`.

### select_daily_ema
This step selects only the daily EMA from `survey` collection. It forms a table `survey_daily_ema`. But it needs more processing.

### widen_daily_ema
This step makes a pivot table style collection. It transforms the `survey_daily_ema` collection.

### copy_daily_ema
This step copies the information from `survey_daily_ema` to `daily` collection for each construct.

### transform_bout_planning_ema_decision

### select_bout_planning_ema
This step selects only Bout Planning EMA Surveys from `survey` collection and all decisions in `survey_bout_planning_ema` and join them. To match, it uses the timestamps. From `survey` collection, it uses `when_asked` key, and from `survey_bout_planning_ema` collection, it uses `when_created_local_dt` key. They are not exactly the same, so it uses 90-min window for the delayed delivery. Thus, by definition, `when_asked` is later than `when_created_local_dt` because survey message is the outcome of the decision made by the algorithms. If the time gap does not exceed 90 minutes, the first survey message is chosen to be matched.

To track the matched survey message, the matching function returns the message uuid encoded in the field of `survey_id` of `survey` collection.




### fill_daily_nans

### transform_message