import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { DailySummaryComponent } from './daily-summary.component';
import { DailySummaryService } from './daily-summary.service';
import { DailyActivitiesUpdateComponent } from './daily-activities-update';
import { DailySummarySerializer } from './daily-summary.serializer';
import { ActivityLogModule } from '@heartsteps/activity-logs/activity-logs.module';
import { ActivitySummaryService } from './activity-summary.service';
import { BackgroundMode } from '@ionic-native/background-mode/ngx';

@NgModule({
    imports: [
        ActivityLogModule,
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
        BackgroundMode,
        ActivitySummaryService,
        DailySummaryService,
        DailySummarySerializer
    ]
})
export class DailySummaryModule {}
