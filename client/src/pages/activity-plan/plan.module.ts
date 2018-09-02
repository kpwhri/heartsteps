import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { PlanPage } from './plan.page';
import { HeartstepsModule } from '@heartsteps/heartsteps.module';
import { PlanModal } from '@pages/activity-plan/plan.modal';
import { PlanComponent } from '@pages/activity-plan/plan.component';
import { DayPlanComponent } from '@pages/activity-plan/day-plan.component'; 

@NgModule({
  declarations: [
    PlanPage,
    PlanModal,
    PlanComponent,
    DayPlanComponent
  ],
  entryComponents: [
    PlanModal,
    DayPlanComponent
  ],
  imports: [
    HeartstepsModule,
    IonicPageModule.forChild(PlanPage),
  ],
  exports: [
    PlanComponent,
    DayPlanComponent
  ]
})
export class ActivityPlanModule {}
