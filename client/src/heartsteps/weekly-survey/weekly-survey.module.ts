import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { IonicPageModule } from 'ionic-angular';
import { ReflectionTimeService } from './reflection-time.service';
import { WeeklyReflectionTimePage } from './weekly-reflection-time.page';
import { WeekService } from './week.service';
import { WeeklyGoalComponent } from './weekly-goal.component';
import { CurrentWeekService } from './current-week.service';
import { WeeklySurveyService } from './weekly-survey.service';
import { LocalNotifications } from '@ionic-native/local-notifications';

@NgModule({
    imports: [
        InfrastructureModule,
        BrowserModule,
        IonicPageModule.forChild(WeeklyGoalComponent),
        IonicPageModule.forChild(WeeklyReflectionTimePage),
    ],
    providers: [
        ReflectionTimeService,
        WeekService,
        CurrentWeekService,
        WeeklySurveyService,
        LocalNotifications
    ],
    declarations: [
        WeeklyReflectionTimePage,
        WeeklyGoalComponent
    ],
    exports: [
        WeeklyReflectionTimePage,
        WeeklyGoalComponent
    ]
})
export class WeeklySurveyModule {}
