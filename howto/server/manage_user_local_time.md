# How to convert server time to user's local datetime

## Goals
* Convert user's local datetime to server time (i.e., setting time-scheduler)
* Convert server's time to user's local datetime (i.e., sending notification)

## Requirements
* Knowledge on how timezone works
* Smartphone's world time app (or similar)

## Short Answer
* Use DayService class and service.get_current_datetime()

## Long Answer
* It's not that long. 

      from datetime import datetime
      from days.services import DayService

      ...
      
      service = DayService(self.user)
      
      # what time is it now there?
      user_local_time = service.get_current_datetime()

* Using timezone
      
      from datetime import datetime
      from days.services import DayService

      ...

      service = DayService(self.user)

      # what timezone is the user in?
      tz = service.service.get_current_timezone()
      
      # getting local time
      time = datetime.now(self.timezone).replace(
            hour = hour,
            minute = minute
        )      

## See Also
* to be updated