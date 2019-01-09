import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { DailySummaryComponent } from '@heartsteps/activity/daily-summary.component';
import { BrowserModule } from '@angular/platform-browser';
import { DailySummaryService } from './daily-summary.service';
import { DailyActivitiesUpdateComponent } from './daily-activities-update';
import { ActivityTypeComponent } from './activity-type.component';
import { ActivityTypeService } from './activity-type.service';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule
    ],
    declarations: [
        ActivityTypeComponent,
        DailySummaryComponent,
        DailyActivitiesUpdateComponent
    ],
    exports: [
        ActivityTypeComponent,
        DailySummaryComponent,
        DailyActivitiesUpdateComponent
    ],
    providers: [
        DailySummaryService,
        ActivityTypeService
    ]
})
export class ActivityModule {}
