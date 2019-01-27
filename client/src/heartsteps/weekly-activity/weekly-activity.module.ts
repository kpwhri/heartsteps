import { NgModule } from '@angular/core';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { WeeklyProgressComponent } from './weekly-progress.component';
import { BrowserModule } from '@angular/platform-browser';
import { ActivityPlansModule } from '@heartsteps/activity-plans/activity-plans.module';
import { ActivityModule } from '@heartsteps/activity/activity.module';
import { CurrentActivityLogService } from './current-activity-log.service';

@NgModule({
    imports: [
        BrowserModule,
        ActivityModule,
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
        CurrentActivityLogService
    ]
})
export class WeeklyActivityModule {}
