import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { HomePage } from './home';
import { DashboardModule } from '@pages/dashboard/dashboard.module';
import { ActivityPlanModule } from '@pages/activity-plan/plan.module';
import { ActivityLogModule } from '@pages/activity-log/activity-log.module';
import { ResourceLibraryModule } from '@pages/resource-library/resource-library.module';
import { DashboardPage } from '@pages/dashboard/dashboard';
import { PlanPage } from '@pages/activity-plan/plan.page';
import { ActivityLogPage } from '@pages/activity-log/activity-log';
import { ResourceLibraryPage } from '@pages/resource-library/resource-library';

@NgModule({
  declarations: [
    HomePage
  ],
  entryComponents: [
    DashboardPage,
    PlanPage,
    ActivityLogPage,
    ResourceLibraryPage
  ],
  imports: [
    DashboardModule,
    ActivityPlanModule,
    ActivityLogModule,
    ResourceLibraryModule,
    IonicPageModule.forChild(HomePage)
  ]
})
export class HomePageModule {}
