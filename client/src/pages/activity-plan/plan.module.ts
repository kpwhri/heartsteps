import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { PlanPage } from './plan';
import { DayPlanComponent } from '@pages/activity-plan/day-plan.component';
import { HeartstepsModule } from '@heartsteps/heartsteps.module';

@NgModule({
  declarations: [
    PlanPage,
    DayPlanComponent
  ],
  imports: [
    HeartstepsModule,
    IonicPageModule.forChild(PlanPage),
  ],
})
export class ActivityPlanModule {}
