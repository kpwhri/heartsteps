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
import { BrowserModule } from '@angular/platform-browser';
import { SettingsModule } from '@pages/settings/settings.module';
import { SettingsPage } from '@pages/settings/settings-page';
import { StatsPage } from './stats.page';
import { CurrentWeekResolver } from './current-week.resolver';
import { ActivityPlanPageModule } from '@pages/activity-plan/plan.module';
import { CurrentDailySummaryResolver } from './current-daily-summary.resolver';
import { HomeGuard } from './home.guard';

const routes:Routes = [
    {
        path: 'home',
        component: HomePage,
        canActivate: [
            HomeGuard
        ],
        children: [{
            path: 'dashboard',
            component: DashboardPage,
            resolve: {
                currentWeek: CurrentWeekResolver
            }
        }, {
            path: 'stats',
            component: StatsPage,
            resolve: {
                summaries: CurrentDailySummaryResolver
            }
        }, {
            path: 'planning',
            component: PlanPage,
            resolve: {
                currentWeek: CurrentWeekResolver
            }
        }, {
            path: 'library',
            component: ResourceLibraryPage
        }, {
            path: 'settings',
            component: SettingsPage
        }, {
            path: '',
            redirectTo: 'dashboard',
            pathMatch: 'full'
        }]
    }
]

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
        CurrentWeekResolver,
        CurrentDailySummaryResolver,
        HomeGuard
    ],
    imports: [
        DashboardModule,
        ActivityPlanPageModule,
        ActivityLogPageModule,
        ResourceLibraryModule,
        SettingsModule,
        BrowserModule,
        IonicPageModule.forChild(HomePage),
        RouterModule.forChild(routes)
    ],
    exports: [
        HomePage,
        RouterModule
    ]
})
export class HomePageModule {}
