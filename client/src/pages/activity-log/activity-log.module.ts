import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ActivityLogPage } from './activity-log.page';
import { ActivityModule } from '@heartsteps/activity/activity.module';
import { RouterModule, Routes } from '@angular/router';
import { ActivitySummaryPage } from './activity-summary.page';
import { ActivitySummaryListComponent } from './activity-summary-list.component';
import { StatsPage } from './stats.page';
import { ActivityLogModule } from '@heartsteps/activity-logs/activity-logs.module';

const routes: Routes = [{
  path: 'activities/:date',
  component: ActivitySummaryPage
}, {
  path: 'activities/logs/:id',
  component: ActivityLogPage
}]

@NgModule({
  declarations: [
    ActivityLogPage,
    ActivitySummaryPage,
    ActivitySummaryListComponent,
    StatsPage
  ],
  imports: [
    ActivityModule,
    ActivityLogModule,
    IonicPageModule.forChild(ActivityLogPage),
    RouterModule.forChild(routes)
  ],
  exports: [
    RouterModule,
    StatsPage
  ]
})
export class ActivityLogPageModule {}
