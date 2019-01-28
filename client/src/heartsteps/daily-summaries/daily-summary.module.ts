import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { DailySummaryComponent } from './daily-summary.component';
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
export class DailySummaryModule {}
