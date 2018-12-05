import { NgModule, forwardRef } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { DailySummaryComponent } from '@heartsteps/activity/daily-summary.component';
import { BrowserModule } from '@angular/platform-browser';
import { WeeklyProgressComponent } from './weekly-progress.component';
import { DailySummaryService } from './daily-summary.service';
import { PlanModal } from './plan.modal';
import { PlanComponent } from './plan.component';
import { DayPlanComponent } from './day-plan.component';
import { IonicPageModule } from 'ionic-angular';
import { ActivityPlanService } from './activity-plan.service';
import { DailyActivitiesUpdateComponent } from './daily-activities-update';
import { ActivityTypeComponent } from './activity-type.component';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        IonicPageModule.forChild(PlanModal),
        IonicPageModule.forChild(PlanComponent),
        IonicPageModule.forChild(DayPlanComponent)
    ],
    declarations: [
        ActivityTypeComponent,
        DailySummaryComponent,
        WeeklyProgressComponent,
        PlanModal,
        PlanComponent,
        DayPlanComponent,
        DailyActivitiesUpdateComponent
    ],
    exports: [
        ActivityTypeComponent,
        DailySummaryComponent,
        WeeklyProgressComponent,
        PlanModal,
        PlanComponent,
        DayPlanComponent,
        DailyActivitiesUpdateComponent
    ],
    providers: [
        DailySummaryService,
        ActivityPlanService
    ]
})
export class ActivityModule {}
