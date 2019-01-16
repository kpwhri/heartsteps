import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { DashboardPage } from './dashboard';
import { ActivityModule } from '@heartsteps/activity/activity.module';
import { WeeklyActivityModule } from '@heartsteps/weekly-activity/weekly-activity.module';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { ActivityPlansModule } from '@heartsteps/activity-plans/activity-plans.module';
import { MorningMessageModule } from '@heartsteps/morning-message/morning-message.module';

@NgModule({
  declarations: [
    DashboardPage
  ],
  imports: [
    ActivityModule,
    ActivityPlansModule,
    MorningMessageModule,
    WeeklySurveyModule,
    WeeklyActivityModule,
    IonicPageModule.forChild(DashboardPage)
  ]
})
export class DashboardModule {}
