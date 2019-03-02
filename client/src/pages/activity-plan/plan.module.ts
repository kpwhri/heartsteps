import { NgModule } from '@angular/core';
import { ActivityPlansModule } from '@heartsteps/activity-plans/activity-plans.module';
import { Routes, RouterModule } from '@angular/router';
import { ActivityPlanEditPage } from './activity-plan-edit.page';
import { ActivityPlanResolver } from './activity-plan.resolver';
import { DayPlanComponent } from './day-plan.component';
import { WeeklyPlanComponent } from './weekly-plan.component';
import { BrowserModule } from '@angular/platform-browser';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { ActivityPlanCompletePage } from './activity-plan-complete.page';

const routes: Routes = [
  {
    path: 'plans/edit/:id',
    component: ActivityPlanEditPage,
    resolve: {
      activityPlan: ActivityPlanResolver
    }
  }, {
    path: 'plans/complete/:id',
    component: ActivityPlanCompletePage,
    resolve: {
      activityPlan: ActivityPlanResolver
    }
  }
];

@NgModule({
  declarations: [
    DayPlanComponent,
    WeeklyPlanComponent,
    ActivityPlanEditPage,
    ActivityPlanCompletePage
  ],
  entryComponents: [
    DayPlanComponent,
    WeeklyPlanComponent
  ],
  exports: [
    DayPlanComponent,
    RouterModule,
    WeeklyPlanComponent
  ],
  imports: [
    ActivityPlansModule,
    HeartstepsComponentsModule,
    BrowserModule,
    RouterModule.forChild(routes)
  ],
  providers: [
    ActivityPlanResolver
  ]
})
export class ActivityPlanPageModule {}
