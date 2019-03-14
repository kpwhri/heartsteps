import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';

import { IonicApp, IonicModule } from 'ionic-angular';
import { SplashScreen } from '@ionic-native/splash-screen';
import { StatusBar } from '@ionic-native/status-bar';

import { MyApp } from './app.component';

import { WelcomePageModule } from '../pages/welcome/welcome.module';
import { OnboardPageModule } from '../pages/onboard/onboard.module';
import { NotificationService } from '@app/notification.service';
import { BackgroundService } from '@app/background.service';
import { LocationService } from '@heartsteps/locations/location.service';
import { HomePageModule } from '@pages/home/home.module';
import { NotificationsModule as NotificationsPageModule } from '@pages/notifications/notifications.module';
import { AuthorizationService } from './authorization.service';
import { NotificationsModule } from '@heartsteps/notifications/notifications.module';
import { WeeklySurveyModule } from '@pages/weekly-survey/weekly-survey.module';
import { MorningSurveyPageModule } from '@pages/morning-survey/morning-survey.module';
import { CurrentWeekModule } from '@heartsteps/current-week/current-week.module';

const appRoutes:Routes = [{
  path: '',
  redirectTo: '/home/dashboard',
  pathMatch: 'full'
}]

@NgModule({
  declarations: [
    MyApp
  ],
  imports: [
    WelcomePageModule,
    CurrentWeekModule.forRoot(),
    OnboardPageModule,
    HomePageModule,
    NotificationsModule,
    NotificationsPageModule,
    WeeklySurveyModule,
    MorningSurveyPageModule,
    BrowserAnimationsModule,
    IonicModule.forRoot(MyApp),
    RouterModule.forRoot(
      appRoutes,
      {
        useHash: true
      }
    )
  ],
  bootstrap: [IonicApp],
  entryComponents: [
    MyApp
  ],
  providers: [
    StatusBar,
    SplashScreen,
    NotificationService,
    BackgroundService,
    LocationService,
    AuthorizationService
  ]
})
export class AppModule {}
