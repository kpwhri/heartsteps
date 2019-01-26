import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { DailySummaryComponent } from '@heartsteps/activity/daily-summary.component';
import { BrowserModule } from '@angular/platform-browser';
import { DailySummaryService } from './daily-summary.service';
import { DailyActivitiesUpdateComponent } from './daily-activities-update';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule
    ],
    declarations: [
        DailySummaryComponent,
        DailyActivitiesUpdateComponent
    ],
    exports: [
        DailySummaryComponent,
        DailyActivitiesUpdateComponent
    ],
    providers: [
        DailySummaryService,
    ]
})
export class ActivityModule {}
