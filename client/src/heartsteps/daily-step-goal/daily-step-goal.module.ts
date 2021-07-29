import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { DailySummaryComponent } from '@heartsteps/daily-summaries/daily-summary.component';

import { DailyStepGoalComponent } from './daily-step-goal.component'

@NgModule({
    declarations: [
        DailyStepGoalComponent
    ],
    exports: [
        DailyStepGoalComponent
    ],
    entryComponents: [
        DailyStepGoalComponent
    ],
    imports: [
        BrowserModule,
        InfrastructureModule
    ],
    providers: [
        DailySummaryComponent
    ]
})
export class DailyStepGoalModule {}
