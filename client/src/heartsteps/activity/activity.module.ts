import { NgModule } from '@angular/core';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { DailySummaryComponent } from '@heartsteps/activity/daily-summary.component';
import { BrowserModule } from '@angular/platform-browser';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
    ],
    declarations: [
        DailySummaryComponent
    ],
    exports: [
        DailySummaryComponent
    ]
})
export class ActivityModule {}
