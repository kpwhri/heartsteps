import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { DashboardPage } from './dashboard';
import { ActivityModule } from '@heartsteps/activity/activity.module';
import { WeeklyActivityModule } from '@heartsteps/weekly-activity/weekly-activity.module';

@NgModule({
  declarations: [
    DashboardPage
  ],
  imports: [
    ActivityModule,
    WeeklyActivityModule,
    IonicPageModule.forChild(DashboardPage)
  ]
})
export class DashboardModule {}
