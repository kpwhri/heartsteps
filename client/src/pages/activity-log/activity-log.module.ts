import { NgModule } from '@angular/core';
import { ActivityLogPage } from './activity-log.page';
import { RouterModule, Routes } from '@angular/router';
import { ActivitySummaryPage } from './activity-summary.page';
import { DailySummaryListComponent } from './daily-summary-list.component';
import { ActivityLogModule } from '@heartsteps/activity-logs/activity-logs.module';
import { ActivityLogResolver } from './activity-log.resolver';
import { DailySummaryModule } from '@heartsteps/daily-summaries/daily-summary.module';
import { DayActivityLogsResolver } from './day-activity-logs.resolver';
import { DailySummaryResolver } from './daily-summary.resolver';
import { FormModule } from '@infrastructure/form/form.module';
import { HeartstepsComponentsModule } from '@infrastructure/components/components.module';
import { BrowserModule } from '@angular/platform-browser';
import { ActivityLogFieldComponent } from './activity-log-field.component';
import { ReactiveFormsModule } from '@angular/forms';
import { ActivityTypeModule } from '@heartsteps/activity-types/activity-types.module';
import { DailySummaryComponent } from './daily-summary.component';
import { ActivityLogCreatePage } from './activity-log-create.page';

const routes: Routes = [{
  path: 'activities/:date',
  component: ActivitySummaryPage,
  resolve: {
    'dailySummary': DailySummaryResolver,
    'activityLogs': DayActivityLogsResolver
  }
}, {
  path: 'activities/logs/create',
  component: ActivityLogCreatePage,
  outlet: 'modal'
}, {
  path: 'activities/logs/:id',
  component: ActivityLogPage,
  resolve: {
    'activityLog': ActivityLogResolver
  },
  outlet: 'modal'
}]

@NgModule({
  declarations: [
    ActivityLogPage,
    ActivityLogCreatePage,
    ActivitySummaryPage,
    DailySummaryComponent,
    DailySummaryListComponent,
    ActivityLogFieldComponent
  ],
  providers: [
    ActivityLogResolver,
    DailySummaryResolver,
    DayActivityLogsResolver,
  ],
  imports: [
    ActivityTypeModule,
    BrowserModule,
    HeartstepsComponentsModule,
    DailySummaryModule,
    ActivityLogModule,
    FormModule,
    ReactiveFormsModule,
    RouterModule.forChild(routes)
  ],
  exports: [
    RouterModule,
    DailySummaryComponent,
    DailySummaryListComponent
  ]
})
export class ActivityLogPageModule {}
