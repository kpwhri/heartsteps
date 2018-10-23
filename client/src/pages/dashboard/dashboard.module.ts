import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { DashboardPage } from './dashboard';
import { ActivityModule } from '@heartsteps/activity/activity.module';

@NgModule({
  declarations: [
    DashboardPage
  ],
  imports: [
    ActivityModule,
    IonicPageModule.forChild(DashboardPage)
  ]
})
export class DashboardModule {}
