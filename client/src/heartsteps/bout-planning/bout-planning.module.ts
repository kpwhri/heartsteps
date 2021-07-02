import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { IonicPageModule } from 'ionic-angular';
// import { ReflectionTimeService } from './reflection-time.service';
import { FirstBoutPlanningTimeService } from './first-bout-planning-time.service';
// import { WeeklyReflectionTimePage } from './weekly-reflection-time.page';
import { FirstBoutPlanningTimePage } from './first-bout-planning-time.page';
// import { WeekService } from './week.service';
// import { WeeklyGoalComponent } from './weekly-goal.component';
// import { WeeklySurveyService } from './weekly-survey.service';
import { FormModule } from '@infrastructure/form/form.module';
// import { WeekSerializer } from './week.serializer';

@NgModule({
    imports: [
        InfrastructureModule,
        FormModule,
        BrowserModule,
        // IonicPageModule.forChild(WeeklyGoalComponent),
        // IonicPageModule.forChild(WeeklyReflectionTimePage),
        IonicPageModule.forChild(FirstBoutPlanningTimePage),
    ],
    providers: [
        // ReflectionTimeService,
        FirstBoutPlanningTimeService,
        // WeekService,
        // WeeklySurveyService,
        // WeekSerializer
    ],
    declarations: [
        // WeeklyReflectionTimePage,
        FirstBoutPlanningTimePage,
        // WeeklyGoalComponent
    ],
    exports: [
        // WeeklyReflectionTimePage,
        FirstBoutPlanningTimePage,
        // WeeklyGoalComponent
    ]
})
export class BoutPlanningModule {}
