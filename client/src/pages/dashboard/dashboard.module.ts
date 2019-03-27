import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { DashboardPage } from './dashboard';
import { CurrentWeekModule } from '@heartsteps/current-week/current-week.module';
import { WeeklySurveyModule } from '@heartsteps/weekly-survey/weekly-survey.module';
import { ActivityPlanPageModule } from '@pages/activity-plan/plan.module';
import { MorningMessageModule } from '@heartsteps/morning-message/morning-message.module';
import { DailySummaryModule } from '@heartsteps/daily-summaries/daily-summary.module';
import { AnchorMessageModule } from '@heartsteps/anchor-message/anchor-message.module';

@NgModule({
  declarations: [
    DashboardPage
  ],
  imports: [
    ActivityPlanPageModule,
    AnchorMessageModule,
    DailySummaryModule,
    MorningMessageModule,
    WeeklySurveyModule,
    CurrentWeekModule,
    IonicPageModule.forChild(DashboardPage)
  ]
})
export class DashboardModule {}
