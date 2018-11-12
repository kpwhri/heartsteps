import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { DailySummaryComponent } from '@heartsteps/activity/daily-summary.component';
import { BrowserModule } from '@angular/platform-browser';
import { WeeklyProgressComponent } from './weekly-progress.component';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
    ],
    declarations: [
        DailySummaryComponent,
        WeeklyProgressComponent
    ],
    exports: [
        DailySummaryComponent,
        WeeklyProgressComponent
    ]
})
export class ActivityModule {}
