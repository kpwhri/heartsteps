import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { PlanPage } from './plan.page';
import { ActivityPlansModule } from '@heartsteps/activity-plans/activity-plans.module';

@NgModule({
  declarations: [
    PlanPage
  ],
  imports: [
    ActivityPlansModule,
    IonicPageModule.forChild(PlanPage),
  ],
  exports: [
    PlanPage
  ]
})
export class ActivityPlanPageModule {}
