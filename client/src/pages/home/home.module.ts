import { NgModule } from "@angular/core";
import { IonicPageModule } from "ionic-angular";
import { HomePage } from "./home";
import { ActivityLogPageModule } from "@pages/activity-log/activity-log.module";
import { ResourceLibraryModule } from "@pages/resource-library/resource-library.module";
import { PlanPage } from "./plan.page";
import { ResourceLibraryPage } from "@pages/resource-library/resource-library";
import { Routes, RouterModule } from "@angular/router";
import { BrowserModule } from "@angular/platform-browser";
import { SettingsModule } from "@pages/settings/settings.module";
import { CurrentWeekResolver } from "./current-week.resolver";
import { ActivityPlanPageModule } from "@pages/activity-plan/plan.module";
import { HomeGuard } from "./home.guard";
import { DashboardPage } from "./dashboard.page";
import { CurrentWeekModule } from "@heartsteps/current-week/current-week.module";
import { AnchorMessageModule } from "@heartsteps/anchor-message/anchor-message.module";
import { DailySummaryModule } from "@heartsteps/daily-summaries/daily-summary.module";
import { ActivitiesPage } from "./activities.page";
import { DashboardNotificationComponent } from "./dashboard-notifications.component";
import { SettingsComponent } from "@pages/settings/settings.component";
import { NotificationCenterModule } from "@heartsteps/notification-center/notification-center.module";
import { NotificationCenterPage } from "./notification-center";

const routes: Routes = [
    {
        path: "home",
        component: HomePage,
        canActivate: [HomeGuard],
        children: [
            {
                path: "dashboard",
                component: DashboardPage,
            },
            {
                path: "activities",
                component: ActivitiesPage,
            },
            {
                path: "planning",
                component: PlanPage,
                resolve: {
                    currentWeek: CurrentWeekResolver,
                },
            },
            {
                path: "library",
                component: ResourceLibraryPage,
            },
            {
                path: "settings",
                component: SettingsComponent,
            },
            {
                path: "notification-center",
                component: NotificationCenterPage,
            },
            {
                path: "",
                redirectTo: "dashboard",
                pathMatch: "full",
            },
        ],
    },
];

@NgModule({
    declarations: [
        HomePage,
        DashboardPage,
        DashboardNotificationComponent,
        PlanPage,
        ActivitiesPage,
        NotificationCenterPage,
    ],
    providers: [CurrentWeekResolver, HomeGuard],
    imports: [
        ActivityPlanPageModule,
        ActivityLogPageModule,
        AnchorMessageModule,
        CurrentWeekModule,
        DailySummaryModule,
        ResourceLibraryModule,
        SettingsModule,
        BrowserModule,
        NotificationCenterModule,
        IonicPageModule.forChild(HomePage),
        RouterModule.forChild(routes),
    ],
    exports: [HomePage, RouterModule],
})
export class HomePageModule {}
