import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { DailySummaryComponent } from '@heartsteps/activity/daily-summary.component';
import { BrowserModule } from '@angular/platform-browser';
import { DailySummaryService } from './daily-summary.service';
import { PlanModal } from './plan.modal';
import { PlanComponent } from './plan.component';
import { DayPlanComponent } from './day-plan.component';
import { IonicPageModule } from 'ionic-angular';
import { ActivityPlanService } from './activity-plan.service';
import { DailyActivitiesUpdateComponent } from './daily-activities-update';
import { ActivityTypeComponent } from './activity-type.component';
import { ActivityLogService } from './activity-log.service';
import { ActivityLogComponent } from './activity-log.component';

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
        PlanModal,
        PlanComponent,
        DayPlanComponent,
        DailyActivitiesUpdateComponent,
        ActivityLogComponent
    ],
    exports: [
        ActivityTypeComponent,
        DailySummaryComponent,
        PlanModal,
        PlanComponent,
        DayPlanComponent,
        DailyActivitiesUpdateComponent,
        ActivityLogComponent
    ],
    providers: [
        DailySummaryService,
        ActivityPlanService,
        ActivityLogService
    ]
})
export class ActivityModule {}
