import { NgModule } from '@angular/core';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { WeeklyProgressComponent } from './weekly-progress.component';
import { ActivityModule } from '@heartsteps/activity/activity.module';

@NgModule({
    imports: [
        ActivityModule,
        WeeklySurveyModule
    ],
    providers: [

    ],
    declarations: [
        WeeklyProgressComponent
    ],
    exports: [
        WeeklyProgressComponent
    ]
})
export class WeeklyActivityModule {}
