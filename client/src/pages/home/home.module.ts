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
import { Routes, RouterModule } from '@angular/router';
import { AuthorizationGaurd, OnboardGaurd } from '@heartsteps/participants/auth-gaurd.service';
import { BrowserModule } from '@angular/platform-browser';

const homeRoutes: Routes = [{
    path: 'home',
    component: HomePage,
    canActivate: [AuthorizationGaurd, OnboardGaurd],
    children: [{
        path: 'dashboard',
        component: DashboardPage
    }, {
        path: 'stats',
        component: ActivityLogPage
    }, {
        path: 'planning',
        component: PlanPage
    }, {
        path: 'learn',
        component: ResourceLibraryPage
    }, {
        path: '**',
        redirectTo: 'dashboard'
    }]
}]

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
        BrowserModule,
        IonicPageModule.forChild(HomePage),
        RouterModule.forChild(homeRoutes)
    ],
    exports: [
        RouterModule
    ]
})
export class HomePageModule {}
