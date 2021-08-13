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
  3. the timing of the task (i.e., when to execute during the day) is determined by a certain DB-based object (i.e., Configuration)


* Decide what class contains the parameters for the task. I'm going to use ***bout_planning_notification/FirstBoutPlanningTime***.

* Let's create a corresponding test before we start. The test will placed in the bout_planning_notification/test directory.

      def test_create_daily_task_1(self):
          # The following statement will create a FirstBoutPlanningTime as 8:00.
          # This means, 4 Daily Tasks will be created at 8am, 11am, 2pm, and 5pm
          FirstBoutPlanningTime.create(self.user, time="08:00")
          
          daily_task_list = FirstBoutPlanningTime.get_daily_tasks(self.user)
          
          self.assertEquals(len(daily_task_list), 4)
          self.assertEquals(daily_task_list[0].time, "08:00")
          self.assertEquals(daily_task_list[1].time, "11:00")
          self.assertEquals(daily_task_list[2].time, "14:00")
          self.assertEquals(daily_task_list[3].time, "17:00")

      def test_create_daily_task_2(self):
          # The following statement will create a FirstBoutPlanningTime as 8:00.
          # This means, 4 Daily Tasks will be created at 8am, 11am, 2pm, and 5pm
          FirstBoutPlanningTime.create(self.user, time="08:00")
          
          # Then, change the first_bout_planning_time to 09:00.
          # This means, existing 4 Daily Tasks will be deleted, and it will create new daily tasks at 9am, 12am, 3pm, and 6pm
          FirstBoutPlanningTime.update(self.user, time="09:00")
          
          daily_task_list = FirstBoutPlanningTime.get_daily_tasks(self.user)
          
          self.assertEquals(len(daily_task_list), 4)
          self.assertEquals(daily_task_list[0].time, "09:00")
          self.assertEquals(daily_task_list[1].time, "12:00")
          self.assertEquals(daily_task_list[2].time, "15:00")
          self.assertEquals(daily_task_list[3].time, "18:00")

* Let's try to run the test. We have a great testing suite: server/keep_testing.sh. Go into the server container, run it with the package. It will run testing command again and again when we change any .py file in the server directory.

$ ./keep_testing.sh bout_planning_notification

* It will generate an exception. (Because we haven't made the method)

```
======================================================================
ERROR: test_create_daily_task_1 (bout_planning_notification.tests.test_first_bout_planning_time_model_test.FirstBoutPlanningTimeModelTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/server/bout_planning_notification/tests/test_first_bout_planning_time_model_test.py", line 381, in test_create_daily_task_1
    daily_task_list = FirstBoutPlanningTime.get_daily_tasks(self.user)
AttributeError: type object 'FirstBoutPlanningTime' has no attribute 'get_daily_tasks'

======================================================================
ERROR: test_create_daily_task_2 (bout_planning_notification.tests.test_first_bout_planning_time_model_test.FirstBoutPlanningTimeModelTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/server/bout_planning_notification/tests/test_first_bout_planning_time_model_test.py", line 398, in test_create_daily_task_2
    daily_task_list = FirstBoutPlanningTime.get_daily_tasks(self.user)
AttributeError: type object 'FirstBoutPlanningTime' has no attribute 'get_daily_tasks'
```

* Let's implement it then. 
  * Add the following import to the ./models.py

        from daily_tasks.models import DailyTask

  * Add the following implementation to the FirstBoutPlanning class.

        def get_daily_tasks(user):
            """This will fetch all daily tasks for the user.
            
            Returns:
                DailyTask[]
            """
            
            # It converts username to user object (if provided) If User object is provided, it will return the user itself.
            user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)
            
            # TODO: We will change the query later
            task_list = DailyTask.objects.filter(user=user_obj).all()
            
            return task_list

* When you save this, the ***keep_testing.sh*** will automatically run the test again. Let's see the result:

```
======================================================================
FAIL: test_create_daily_task_1 (bout_planning_notification.tests.test_first_bout_planning_time_model_test.FirstBoutPlanningTimeModelTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/server/bout_planning_notification/tests/test_first_bout_planning_time_model_test.py", line 383, in test_create_daily_task_1
    self.assertEquals(len(daily_task_list), 4)
AssertionError: 0 != 4

======================================================================
FAIL: test_create_daily_task_2 (bout_planning_notification.tests.test_first_bout_planning_time_model_test.FirstBoutPlanningTimeModelTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/server/bout_planning_notification/tests/test_first_bout_planning_time_model_test.py", line 400, in test_create_daily_task_2
    self.assertEquals(len(daily_task_list), 4)
AssertionError: 0 != 4
```

* OK. Now it's bringing the task right. But since we haven't created DailyTasks, so nothing has been returned. Let's work on that.

* We are trying to link a **create/update** operation on FirstBoutPlanningTime object's **save()** operation. (Right?) There are two, or three ways to do it: (a) Overriding the save() method, (b) using pre_save signal, and (c) using post_save signal. For now, we will use (c) approach.

* To do that, we got three things to do.

  * Create ***bout_planning_notification/receivers.py***

        from django.dispatch import receiver
        from django.db.models.signals import post_save
        from .models import FirstBoutPlanningTime
        
        @receiver(post_save, sender=FirstBoutPlanningTime)
        def FeatureFlags_updated(instance, created, **kwargs):
            if created:
                # handle the creation
                pass
            else:
                # handle the update
                pass

  * Update ***bout_planning_notification/apps.py***: add the following lines under ***BoutPlanningNotificationConfig*** class

            def ready(self):
                import bout_planning_notification.receivers

  * Update ***bout_planning_notification/\_\_init\_\_.py***

            default_app_config = 'bout_planning_notification.apps.BoutPlanningNotificationConfig'

* This structure gets ***post_save*** signal from FirstBoutPlanningTime class. It will catch the signal **after save()** is called.

* Weirdly, a new receiver is effective after the container is rebooted. Let's reboot them. Edits are effective immediately.

* If you put something like "print()" in the receiver, you might see the effect of it. (use it with /admin pages.)

* Let's create DailyTasks then. First, we will create them when the FirstBoutPlanningTime is created. 
  * Put the following in the "handling creation" part in ./receivers.py.

        # four DailyTasks will be made by three hour gap
        for i in range(instance.hour, instance.hour + 12, 3):
            create_daily_task(instance.user, i)

  * Put the following in imports:

        from daily_tasks.models import DailyTask
        from .models import User

  * Put the following somewhere safe before FeatureFlags_updated()

        def create_daily_task(user, hour, minute=0):
          return DailyTask.create_daily_task(user=user,
                                      category='BOUT_PLANNING',
                                      task='bout_planning_notification.tasks.bout_planning_decision_making',
                                      name='{} BoutPlanningNotificationDecisionMaking {:02} {:02}'.format(user.username, hour, minute),
                                      arguments={"username": user.username},
                                      day=None,
                                      hour=hour,
                                      minute=minute)

  * Let's use current 'bout_planning_notification.tasks.bout_planning_decision_making'. If you'd like, you can use your own task.

* Save everything, then let's see how the test works:

```
======================================================================
FAIL: test_create_daily_task_2 (bout_planning_notification.tests.test_first_bout_planning_time_model_test.FirstBoutPlanningTimeModelTest)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/server/bout_planning_notification/tests/test_first_bout_planning_time_model_test.py", line 401, in test_create_daily_task_2
    self.assertEquals(daily_task_list[0].time, "09:00")
AssertionError: '08:00' != '09:00'
- 08:00
?  ^
+ 09:00
?  ^
```

* Wow, the first failed test is gone. Let's make update part. 
  * This is the code for the update part

        # after deleting the daily tasks,
        delete_daily_task(instance.user)
        first_bout_planning_time = FirstBoutPlanningTime.get(instance.user)
        # four DailyTasks will be newly made by three hour gap
        for i in range(first_bout_planning_time.hour, first_bout_planning_time.hour + 12, 3):
            create_daily_task(instance.user, i)

  * This is the delete_daily_task()

        def delete_daily_task(user):
          daily_task_list = FirstBoutPlanningTime.get_daily_tasks(user)
          
          for daily_task in daily_task_list:
              daily_task.delete_task()

* Yay! All the fails are gone!

```
Using existing test database for alias 'default'...
System check identified no issues (0 silenced).
...................................
----------------------------------------------------------------------
Ran 35 tests in 10.954s

OK
Preserving test database for alias 'default'...
```

* Now, we need to go back to get_daily_tasks() to change.

* It need some restructuring job. First, to reuse TASK_CATEGORY and other constants among non-class methods, we need ./constants.py

      TASK_CATEGORY = 'BOUT_PLANNING'
      TASK_PATH = 'bout_planning_notification.tasks.bout_planning_decision_making'
      TASK_NAME = 'BoutPlanningNotificationDecisionMaking'

* Then, import all (*) from this in the following files
  * ./receivers.py
  * ./models.py
  * ./tasks.py (not necessary for now, but for later)

* Then, we change the ***models.FirstBoutPlanningTime.get_daily_tasks()***

      def get_daily_tasks(user):
          """This will fetch all daily tasks for the user.
          
          Returns:
              DailyTask[]
          """

          # It converts username to user object (if provided) If User object is provided, it will return the user itself.
          user_obj = FirstBoutPlanningTime.convert_to_user_obj(user)

          task_list = DailyTask.search(user=user_obj,
                                      category=receivers.TASK_CATEGORY)

          return list(task_list)

* Finally, add the following to ***/server/heartsteps/celery.py*** under the section ***app.conf.task_routes***.

      ...
      'bout_planning_notification.tasks.*': {
          'queue': 'messages'
      }
      ...

* We did this to enable running the task by celery.

## See Also

* https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html

* https://github.com/kpwhri/heartsteps/blob/master/server/bout_planning_notification/receivers.py

* https://github.com/kpwhri/heartsteps/blob/master/server/bout_planning_notification/models.py#L185

* https://github.com/kpwhri/heartsteps/tree/master/server/daily_tasks