import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { HomePage } from './home';
import { DashboardModule } from '@pages/dashboard/dashboard.module';
import { ActivityPlanPageModule } from '@pages/activity-plan/plan.module';
import { ActivityLogPageModule } from '@pages/activity-log/activity-log.module';
import { ResourceLibraryModule } from '@pages/resource-library/resource-library.module';
import { DashboardPage } from '@pages/dashboard/dashboard';
import { PlanPage } from '@pages/activity-plan/plan.page';
import { ResourceLibraryPage } from '@pages/resource-library/resource-library';
import { Routes, RouterModule } from '@angular/router';
import { AuthorizationGaurd, OnboardGaurd } from '@heartsteps/participants/auth-gaurd.service';
import { BrowserModule } from '@angular/platform-browser';
import { SettingsModule } from '@pages/settings/settings.module';
import { SettingsPage } from '@pages/settings/settings-page';
import { StatsPage } from '@pages/activity-log/stats.page';

const homeRoutes: Routes = [{
    path: 'home',
    component: HomePage,
    canActivate: [AuthorizationGaurd, OnboardGaurd],
    children: [{
        path: 'dashboard',
        component: DashboardPage
    }, {
        path: 'stats',
        component: StatsPage
    }, {
        path: 'planning',
        component: PlanPage
    }, {
        path: 'library',
        component: ResourceLibraryPage
    }, 
    {
        path: 'settings',
        component: SettingsPage
    },
    {
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
        StatsPage,
        ResourceLibraryPage
    ],
    imports: [
        DashboardModule,
        ActivityPlanPageModule,
        ActivityLogPageModule,
        ResourceLibraryModule,
        SettingsModule,
        BrowserModule,
        IonicPageModule.forChild(HomePage),
        RouterModule.forChild(homeRoutes)
    ],
    exports: [
        RouterModule
    ]
})
export class HomePageModule {}
