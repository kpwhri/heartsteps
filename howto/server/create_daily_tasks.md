# How to create/manage/delete a new daily task

## Goal

* Create tasks that run same time of the day (which also consider user's current timezone)

## Requirements

* None

## Simple Answer

* Use ***DailyTask.create_daily_task()***

## Long Answer
I'll assume the contexts to the following:
  1. the task creation will be triggered by one of the following:
      * the creation of a certain Model object (i.e., User,  Configuration)
      * the update of a certain Model object (i.e., User,Configuration)
  2. the task will be deleted if the triggering Model object is deleted.
  3. the timing of the task (i.e., when to execute during the day) is determined by a certain db-based object (i.e., Configuration)


* Decide what class contains
* create a corresponding test before we start
```
