import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { IonicApp, IonicModule } from 'ionic-angular';
import { SplashScreen } from '@ionic-native/splash-screen';
import { StatusBar } from '@ionic-native/status-bar';

import { MyApp } from './app.component';

import { EnrollPageModule } from '../pages/enroll/enroll.module';
import { HeartstepsModule } from '../heartsteps/heartsteps.module';
import { WelcomePageModule } from '../pages/welcome/welcome.module';
import { OnboardPageModule } from '../pages/onboard/onboard.module';
import { NotificationPane } from './notification';
import { NotificationService } from '@app/notification.service';
import { BackgroundService } from '@app/background.service';
import { DashboardModule } from '@pages/dashboard/dashboard.module';

@NgModule({
  declarations: [
    MyApp,
    NotificationPane
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    EnrollPageModule,
    WelcomePageModule,
    OnboardPageModule,
    DashboardModule,
    HeartstepsModule,
    IonicModule.forRoot(MyApp)
  ],
  bootstrap: [IonicApp],
  entryComponents: [
    MyApp,
    NotificationPane
  ],
  providers: [
    StatusBar,
    SplashScreen,
    NotificationService,
    BackgroundService
  ]
})
export class AppModule {}
