import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';

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
    ]
})
export class DailyStepGoalModule {}
