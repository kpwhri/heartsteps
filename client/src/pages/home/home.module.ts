import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { HomePage } from './home';
import { ActivityLogPageModule } from '@pages/activity-log/activity-log.module';
import { ResourceLibraryModule } from '@pages/resource-library/resource-library.module';
import { PlanPage } from './plan.page';
import { ResourceLibraryPage } from '@pages/resource-library/resource-library';
import { Routes, RouterModule } from '@angular/router';
import { BrowserModule } from '@angular/platform-browser';
import { SettingsModule } from '@pages/settings/settings.module';
import { SettingsPage } from '@pages/settings/settings-page';
import { StatsPage } from './stats.page';
import { CurrentWeekResolver } from './current-week.resolver';
import { ActivityPlanPageModule } from '@pages/activity-plan/plan.module';
import { HomeGuard } from './home.guard';
import { DashboardPage } from './dashboard.page';
import { CurrentWeekModule } from '@heartsteps/current-week/current-week.module';
import { AnchorMessageModule } from '@heartsteps/anchor-message/anchor-message.module';
import { DailySummaryModule } from '@heartsteps/daily-summaries/daily-summary.module';
import { AnchorMessageResolver } from './anchor-message.resolver';

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
                anchorMessage: AnchorMessageResolver
            }
        }, {
            path: 'stats',
            component: StatsPage
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
        DashboardPage,
        PlanPage,
        StatsPage
    ],
    providers: [
        AnchorMessageResolver,
        CurrentWeekResolver,
        HomeGuard
    ],
    imports: [
        ActivityPlanPageModule,
        ActivityLogPageModule,
        AnchorMessageModule,
        CurrentWeekModule,
        DailySummaryModule,
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
