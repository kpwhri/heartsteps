import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { RouterModule, Routes } from '@angular/router';
import { WeeklySurveyPage } from './weekly-survey.page';
import { SurveyStartPage } from './survey-start.page';
import { SurveyReviewComponent } from './survey-review.component';
import { WeeklySurveyService } from './weekly-survey.service';
import { GoalComponent } from './goal.component';
import { SurveyComponent } from './survey.component';
import { WeeklySurveyModule as HeartstepsWeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module'
import { WeekResolver } from './week.resolver';
import { NextWeekResolver } from './next-week.resolver';
import { InfrastructureModule } from '@infrastructure/infrastructure.module';

const routes: Routes = [{
  path: 'weekly-survey/:weekId',
  component: WeeklySurveyPage,
  resolve: {
    weeks: WeekResolver
  },
  children: [{
      path: 'start',
      component: SurveyStartPage
  }, {
      path: 'survey',
      component: SurveyComponent
  }, {
      path: 'goal',
      component: GoalComponent
  }, {
      path: 'review',
      component: SurveyReviewComponent
  }, {
    path: '**',
    redirectTo: 'start'
  }]
}];

@NgModule({
  declarations: [
    WeeklySurveyPage,
    SurveyStartPage,
    SurveyReviewComponent,
    GoalComponent,
    SurveyComponent
  ],
  providers: [
      WeeklySurveyService,
      WeekResolver,
      NextWeekResolver
  ],
  imports: [
    InfrastructureModule,
    HeartstepsWeeklySurveyModule,
    IonicPageModule.forChild(WeeklySurveyPage),
    RouterModule.forChild(routes)
  ],
  exports: [
    RouterModule
  ]
})
export class WeeklySurveyModule {}
