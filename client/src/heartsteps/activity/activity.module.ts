import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { DailySummaryComponent } from '@heartsteps/activity/daily-summary.component';
import { BrowserModule } from '@angular/platform-browser';
import { DailySummaryService } from './daily-summary.service';
import { DailyActivitiesUpdateComponent } from './daily-activities-update';
import { ActivityTypeComponent } from './activity-type.component';
import { ActivityLogService } from './activity-log.service';
import { ActivityLogComponent } from './activity-log.component';
import { ActivityTypeService } from './activity-type.service';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule
    ],
    declarations: [
        ActivityTypeComponent,
        DailySummaryComponent,
        DailyActivitiesUpdateComponent,
        ActivityLogComponent
    ],
    exports: [
        ActivityTypeComponent,
        DailySummaryComponent,
        DailyActivitiesUpdateComponent,
        ActivityLogComponent
    ],
    providers: [
        DailySummaryService,
        ActivityLogService,
        ActivityTypeService
    ]
})
export class ActivityModule {}
