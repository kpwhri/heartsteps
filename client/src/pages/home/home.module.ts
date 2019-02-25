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
import { StatsPage } from './stats.page';
import { CurrentWeekResolver } from './current-week.resolver';
import { ActivityPlansModule } from '@heartsteps/activity-plans/activity-plans.module';

const homeRoutes: Routes = [{
        path: 'dashboard',
        component: DashboardPage,
        outlet: 'home'
    }, {
        path: 'stats',
        component: StatsPage,
        outlet: 'home'
    }, {
        path: 'planning',
        component: PlanPage,
        outlet: 'home'
    }, {
        path: 'library',
        component: ResourceLibraryPage,
        outlet: 'home'
    }, {
        path: 'settings',
        component: SettingsPage,
        outlet: 'home'
}];

@NgModule({
    declarations: [
        HomePage,
        PlanPage,
        StatsPage
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
        HomePage,
        RouterModule
    ]
})
export class HomePageModule {}
