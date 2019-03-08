import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { RouterModule, Routes } from '@angular/router';
import { WeeklySurveyPage } from './weekly-survey.page';
import { SurveyStartPage } from './survey-start.page';
import { SurveyComponent } from './survey.component';
import { WeeklySurveyModule as HeartstepsWeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module'
import { WeeklySurveyResolver } from './week.resolver';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';
import { CurrentWeekModule } from '@heartsteps/current-week/current-week.module';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { NextWeekGoalComponent } from './next-week-goal.component';
import { NextWeekPlansComponent } from './next-week-plans.component';
import { ActivityPlanPageModule } from '@pages/activity-plan/plan.module';

const routes: Routes = [
    {
        path: 'weekly-survey/:page',
        component: WeeklySurveyPage,
        resolve: {
            weeklySurvey: WeeklySurveyResolver
        }
    }, {
        path: 'weekly-survey',
        redirectTo: 'weekly-survey/start'
    }
];

@NgModule({
  declarations: [
    WeeklySurveyPage,
    SurveyStartPage,
    NextWeekGoalComponent,
    NextWeekPlansComponent,
    SurveyComponent
  ],
  entryComponents: [
    NextWeekGoalComponent,
    NextWeekPlansComponent,
    SurveyComponent,
    SurveyStartPage
  ],
  providers: [
      WeeklySurveyResolver
  ],
  imports: [
    InfrastructureModule,
    HeartstepsComponentsModule,
    HeartstepsWeeklySurveyModule,
    ActivityPlanPageModule,
    CurrentWeekModule,
    IonicPageModule.forChild(WeeklySurveyPage),
    RouterModule.forChild(routes)
  ],
  exports: [
    RouterModule
  ]
})
export class WeeklySurveyModule {}
