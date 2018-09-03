import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { DashboardPage } from './dashboard';
import { ActivityPlanModule } from '@pages/activity-plan/plan.module';

@NgModule({
  declarations: [
    DashboardPage
  ],
  imports: [
    ActivityPlanModule,
    IonicPageModule.forChild(DashboardPage)
  ]
})
export class DashboardModule {}
