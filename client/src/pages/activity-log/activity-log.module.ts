import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ActivityLogPage } from './activity-log.page';
import { RouterModule, Routes } from '@angular/router';
import { ActivitySummaryPage } from './activity-summary.page';
import { DailySummaryListComponent } from './daily-summary-list.component';
import { ActivityLogModule } from '@heartsteps/activity-logs/activity-logs.module';
import { ActivityLogResolver } from './activity-log.resolver';
import { DailySummaryModule } from '@heartsteps/daily-summaries/daily-summary.module';
import { DayActivityLogsResolver } from './day-activity-logs.resolver';
import { DailySummaryResolver } from './daily-summary.resolver';

const routes: Routes = [{
  path: 'activities/:date',
  component: ActivitySummaryPage,
  resolve: {
    'dailySummary': DailySummaryResolver,
    'activityLogs': DayActivityLogsResolver
  }
}, {
  path: 'activities/logs/:id',
  component: ActivityLogPage,
  resolve: {
    'activityLog': ActivityLogResolver
  }
}]

@NgModule({
  declarations: [
    ActivityLogPage,
    ActivitySummaryPage,
    DailySummaryListComponent
  ],
  providers: [
    ActivityLogResolver,
    DailySummaryResolver,
    DayActivityLogsResolver,
  ],
  imports: [
    DailySummaryModule,
    ActivityLogModule,
    IonicPageModule.forChild(ActivityLogPage),
    RouterModule.forChild(routes)
  ],
  exports: [
    RouterModule,
    DailySummaryListComponent
  ]
})
export class ActivityLogPageModule {}
