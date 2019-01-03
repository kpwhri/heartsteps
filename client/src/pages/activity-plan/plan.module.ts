import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { PlanPage } from './plan.page';
import { ActivityModule } from '@heartsteps/activity/activity.module';
import { WeeklyActivityModule } from '@heartsteps/weekly-activity/weekly-activity.module';

@NgModule({
  declarations: [
    PlanPage
  ],
  imports: [
    ActivityModule,
    WeeklyActivityModule,
    IonicPageModule.forChild(PlanPage),
  ],
  exports: [
    PlanPage
  ]
})
export class ActivityPlanModule {}
