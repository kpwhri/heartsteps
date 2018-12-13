import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ActivityLogPage } from './activity-log';
import { ActivityModule } from '@heartsteps/activity/activity.module';
import { RouterModule, Routes } from '@angular/router';
import { ActivitySummaryPage } from './activity-summary.page';
import { ActivitySummaryListComponent } from './activity-summary-list.component';

const routes: Routes = [{
  path: 'activities/:date',
  component: ActivitySummaryPage
}]

@NgModule({
  declarations: [
    ActivityLogPage,
    ActivitySummaryPage,
    ActivitySummaryListComponent
  ],
  entryComponents: [
    ActivityLogPage
  ],
  imports: [
    ActivityModule,
    IonicPageModule.forChild(ActivityLogPage),
    RouterModule.forChild(routes)
  ],
  exports: [
    RouterModule
  ]
})
export class ActivityLogModule {}
