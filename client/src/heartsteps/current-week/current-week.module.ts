import { NgModule } from '@angular/core';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { WeeklyProgressComponent } from './weekly-progress.component';
import { BrowserModule } from '@angular/platform-browser';
import { ActivityPlansModule } from '@heartsteps/activity-plans/activity-plans.module';
import { CurrentActivityLogService } from './current-activity-log.service';
import { ActivityLogModule } from '@heartsteps/activity-logs/activity-logs.module';
import { CurrentWeekService } from './current-week.service';

@NgModule({
    imports: [
        BrowserModule,
        ActivityLogModule,
        ActivityPlansModule,
        WeeklySurveyModule
    ],
    declarations: [
        WeeklyProgressComponent
    ],
    exports: [
        WeeklyProgressComponent
    ],
    providers: [
        CurrentActivityLogService,
        CurrentWeekService
    ]
})
export class CurrentWeekModule {}
