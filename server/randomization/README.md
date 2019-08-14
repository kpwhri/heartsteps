Activity suggestion randomization documentation. This is a work in progress, please excuse the dust.

Activity suggestion randomization is centered around the Decision model, which is used to track all activity suggestion randomizations and randomized user was treated, and at what probability the user was randomized.

The decision model references contextual objects, which are used to select an appropriate message from the behavioral message models.

## Availability
A user can only be treated if they are available for treatment. To be available for treatment, and participant must meet various availability critera. All reasons for a user being unavailable for treatment are stored as Unavailable Reasons, that reference a specific decision.

* **Unreachable** means the heartsteps-server was unable to create the decision at the time the decision was supposed to be processed. This would happen if no decision context from a participant had been recieved with the **decision time window.**
    - This unavailable reason is often used when a decision was *imputed.*
    - Imputed decision times will mark the participant as unavailable, but will generate context using data that was not available at the decision time.
* **Notification recently sent** means that a notification was sent to the user in the past hour.
* **No step count data** means there was no fitbit-watch-app data available at the time of the decision, so there is no way for the decision to determine if the participant was sedentary.
* **Not sedentary** means the participant has taken more than 150 steps in the past 30 minutes. This uses data that is reported by the fitbit-watch-app.
* **Recently active** means the participant has taken more than 2,000 steps in the past 2 hours. This unavialble check was added to not send notifications to participants if they are resting after doing an activity.
* **On vacation** means the user has set a temporary block on activity suggestions throught the heartsteps-client app.
* **Disabled** means the user has disabled their account, and intentionally left the study.
* **Service error** means there was a technical error while processing the decision.
