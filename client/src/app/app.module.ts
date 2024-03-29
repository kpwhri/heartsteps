import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";

import { HttpClientModule } from '@angular/common/http';

import { IonicApp, IonicModule } from "ionic-angular";
import { SplashScreen } from "@ionic-native/splash-screen";
import { StatusBar } from "@ionic-native/status-bar";

import { MyApp } from "./app.component";

import { WelcomePageModule } from "../pages/welcome/welcome.module";
import { NLMModule } from "../pages/nlm/nlm.module";
import { OnboardPageModule } from "../pages/onboard/onboard.module";
import { NotificationService } from "@app/notification.service";
import { HomePageModule } from "@pages/home/home.module";
import { NotificationsModule as NotificationsPageModule } from "@pages/notifications/notifications.module";
import { AuthorizationService } from "./authorization.service";
import { NotificationsModule } from "@heartsteps/notifications/notifications.module";
import { BoutPlanningModule } from "@pages/bout-planning/bout-planning.module";
import { WeeklySurveyModule } from "@pages/weekly-survey/weekly-survey.module";
import { MorningSurveyPageModule } from "@pages/morning-survey/morning-survey.module";
import { CurrentWeekModule } from "@heartsteps/current-week/current-week.module";

import { UserLogsModule } from "@pages/user-logs/user-logs.module"

import { HeartstepsInfrastructureModule } from "@infrastructure/heartsteps/heartsteps.module";
import { AnalyticsService } from "@infrastructure/heartsteps/analytics.service";
import { SetupPageModule } from "@pages/setup/setup.module";
import { BaselineWeekModule } from "@pages/baseline-week/baseline-week.module";
import { RootComponent } from "./root.component";
import { AppService } from "./app.service";
import { AppReadyResolver } from "./app.resolver";
import { LoadingPageComponent } from "./loading-page.component";
import { HeartstepsComponentsModule } from "@infrastructure/components/components.module";

import { FeatureFlagsModule } from "@heartsteps/feature-flags/feature-flags.module";
import { BoutPlanningSurveysModule } from "@heartsteps/bout-planning/bout-planning-surveys.module";
import { BackgroundMode } from '@ionic-native/background-mode/ngx';

const routes: Routes = [
    {
        path: "loading",
        component: LoadingPageComponent,
    },
    {
        path: "",
        component: RootComponent,
        resolve: {
            ready: AppReadyResolver,
        },
    },
];

@NgModule({
    declarations: [LoadingPageComponent, MyApp, RootComponent],
    imports: [
        HttpClientModule,
        BaselineWeekModule,
        WelcomePageModule,
        NLMModule,
        FeatureFlagsModule,
        CurrentWeekModule,
        OnboardPageModule,
        SetupPageModule,
        HomePageModule,
        UserLogsModule,
        HeartstepsInfrastructureModule,
        HeartstepsComponentsModule,
        NotificationsModule,
        NotificationsPageModule,
        WeeklySurveyModule,
        BoutPlanningModule,
        MorningSurveyPageModule,
        BrowserAnimationsModule,
        BoutPlanningSurveysModule,
        IonicModule.forRoot(MyApp),
        RouterModule.forRoot(routes, {
            useHash: true,
        }),
    ],
    bootstrap: [IonicApp],
    entryComponents: [MyApp],
    providers: [
        BackgroundMode,
        StatusBar,
        SplashScreen,
        NotificationService,
        AuthorizationService,
        AnalyticsService,
        AppService,
        AppReadyResolver,
    ],
})
export class AppModule {}
