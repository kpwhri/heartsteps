import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { HomePage } from './home';
import { DashboardModule } from '@pages/dashboard/dashboard.module';
import { ActivityLogPageModule } from '@pages/activity-log/activity-log.module';
import { ResourceLibraryModule } from '@pages/resource-library/resource-library.module';
import { DashboardPage } from '@pages/dashboard/dashboard';
import { PlanPage } from './plan.page';
import { ResourceLibraryPage } from '@pages/resource-library/resource-library';
import { Routes, RouterModule } from '@angular/router';
import { AuthorizationGaurd, OnboardGaurd } from '@heartsteps/participants/auth-gaurd.service';
import { BrowserModule } from '@angular/platform-browser';
import { SettingsModule } from '@pages/settings/settings.module';
import { SettingsPage } from '@pages/settings/settings-page';
import { StatsPage } from '@pages/activity-log/stats.page';
import { CurrentWeekResolver } from './current-week.resolver';
import { ActivityPlansModule } from '@heartsteps/activity-plans/activity-plans.module';

const homeRoutes: Routes = [{
    path: 'home',
    component: HomePage,
    canActivate: [AuthorizationGaurd, OnboardGaurd],
    resolve: {
        currentWeek: CurrentWeekResolver
    },
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
        HomePage,
        PlanPage
    ],
    entryComponents: [
        DashboardPage,
        PlanPage,
        StatsPage,
        ResourceLibraryPage
    ],
    providers: [
        CurrentWeekResolver
    ],
    imports: [
        DashboardModule,
        ActivityPlansModule,
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
