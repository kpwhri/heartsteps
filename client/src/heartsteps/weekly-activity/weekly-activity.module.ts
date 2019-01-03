import { NgModule } from '@angular/core';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { WeeklyProgressComponent } from './weekly-progress.component';
import { ActivityModule } from '@heartsteps/activity/activity.module';
import { WeeklyPlanComponent } from './weekly-plan.component';
import { BrowserModule } from '@angular/platform-browser';

@NgModule({
    imports: [
        BrowserModule,
        ActivityModule,
        WeeklySurveyModule
    ],
    providers: [

    ],
    declarations: [
        WeeklyProgressComponent,
        WeeklyPlanComponent
    ],
    exports: [
        WeeklyProgressComponent,
        WeeklyPlanComponent
    ]
})
export class WeeklyActivityModule {}
