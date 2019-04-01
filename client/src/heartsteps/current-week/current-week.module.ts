import { NgModule, ModuleWithProviders } from '@angular/core';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { WeeklyProgressComponent } from './weekly-progress.component';
import { BrowserModule } from '@angular/platform-browser';
import { ActivityPlansModule } from '@heartsteps/activity-plans/activity-plans.module';
import { ActivityLogModule } from '@heartsteps/activity-logs/activity-logs.module';
import { CurrentWeekService } from './current-week.service';
import { CurrentDailySummariesService } from './current-daily-summaries.service';
import { DailySummaryModule } from '@heartsteps/daily-summaries/daily-summary.module';

@NgModule({
    imports: [
        BrowserModule,
        ActivityLogModule,
        ActivityPlansModule,
        DailySummaryModule,
        WeeklySurveyModule
    ],
    declarations: [
        WeeklyProgressComponent
    ],
    exports: [
        WeeklyProgressComponent
    ],
    providers: [
        CurrentDailySummariesService,
        CurrentWeekService
    ]
})
export class CurrentWeekModule {

    static forRoot(): ModuleWithProviders {
        return {
            ngModule: CurrentWeekModule,
            providers: [
                CurrentDailySummariesService,
                CurrentWeekService
            ]
        }
    }
}
