## Overview
The HeartSteps server is build with Django, which is primarily configured in the `heartsteps` module.

The *Primary App* in the server is `participants` which defines the Study, Cohort, and Participant models record the seperate study permissions, cohort configurations, and participants who are enrolled in HeartSteps. *Intervention apps* are configured by primary apps (eg participants) and **should** run a behavioral intervention that is designed to be orthagonal to other behavioral interventions. *Infrastructure apps* provide specific utility functions that are reused by other intervention apps.

All participant information is shown on the HeartSteps dashboard is seperated by Study "admins" access to Django user accounts. Non-identifiable information is shown on the default django admin, and should be considered viewable by any Django staff user accounts. The Django superuser account has access to all information in the database.

**NOTE** To aim for a more orthagonal application architecture, the participant model has a one-to-one relationship with the Django User model. This allows other applicaitons to use the Django User model directly without dependency on the participant module -- hopefully supporting more reusable modules. The best way to import the Django User model is with [get_user_model method.](https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#referencing-the-user-model)

## Primary Apps
* `participants` configures the person participating in HeartSteps, which includes starting and stoping interventions and participant authentication.
* `heartsteps_messages` was an attempt to simplify anti-sedentary and walking suggestion orchestration with the fitbit clock face app to a seperate non-participants app (as the participants app is a mess).
* `dashboard` the study dashboard was originally created in a single application that imports models from the participants module. Currently there is too much going on in the dashboard module -- finding ways to seperate and simplify would be rad.

## Intervention Apps
* `activity_logs` is a record of all participant activities that were either detected from fitbit_activities, created from a completed activity-plan, or created from the heartsteps-client.
* `activity_plans` manages activity plans created by the participant in the heartsteps-client.
* `activity_summaries`
* `activity_surveys` when a fitbit activity is detected a survey is sent to the heartsteps-client
* `activity_types`
* `adherence_messages` responsible for sending sms messages to participants when they are not adhereing to study protocol.
* `anti_sedentary` randomizes participant for anti-sedentary notifications when step count is recieved from fitbit clock face app. Communicates with AntiSedentaryService.
* `burst_periods` changes the treatment probabilities for activity_surveys and walking_suggestion_surveys according to a schedule that is created in the `dashboard`.
* `closeout_messages`
* `contact`
* `fitbit_activities` fitbit activity logs, daily metrics, and minute-level metrics for all fitbit accounts.
* `fitbit_activity_logs` connects fitbit activity logs to activity_logs used in heartsteps-client. 
* `fitbit_authorize` manages authorizing fitbit-api with heartsteps-server. Saves records in `fitbit_api`
* `fitbit_clock_face` api that interacts with Fitbit Clock Face app. This *will* replace `pin_gen` and `watch_app` eventually.
* `morning_messages`
* `page_views` manages page views recorded by heartsteps-client
* `pin_gen`
* `walking_suggestion_surveys`
* `walking_suggestion_times`
* `walking_suggestions` manages walking suggestions intervention and communicates with walking suggestion service
* `watch-app`
* `weekly_reflection`
* `weeks`

## Infrastructure Apps
* `behavioral_messages` models for creating and randomizing messages in an intervention
* `daily_tasks` utility for scheduling recurring tasks at specific times of day, recording the results, and adjusting task timing if timezone in `days` changes.
* `days` define service for determining start and end of participant's day depending on timezone.
* `fitbit_api` stores and wraps fitbit account information for user accounts. We allow a mapping of multiple user accounts to a singe fitbit account.
* `locations`
* `push_messages` manages OneSignal integration and manages push notificaion metadata.
* `randomization` reusable decision model and logic used in `anti_sedentary` and `walking_suggestions`
* `service_requests` single app to keeps track of server interaction with outside services (eg AntiSedentaryService, DarkSkyAPI, Fitbit-API)
* `sms_messages` wraps twilio API and keeps track of sent messages
* `surveys`
* `user_event_logs` not really implemented
* `weather` manages weather reports fetched from DarkSky API based on participant location
* `notification_queue` Under development. handles notification queue

## Ugh Apps
* `privacy_policy` needed to put privacy policy to be listed on app store somewhere...
