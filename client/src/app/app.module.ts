import { BrowserModule } from '@angular/platform-browser';
import { ErrorHandler, NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { IonicApp, IonicErrorHandler, IonicModule } from 'ionic-angular';
import { SplashScreen } from '@ionic-native/splash-screen';
import { StatusBar } from '@ionic-native/status-bar';

import { MyApp } from './app.component';

import { EnrollPageModule } from '../pages/enroll/enroll.module';
import { HeartstepsModule } from '../heartsteps/heartsteps.module';
import { WelcomePageModule } from '../pages/welcome/welcome.module';
import { HomePageModule } from '../pages/home/home.module';
import { OnboardPageModule } from '../pages/onboard/onboard.module';
import { NotificationPane } from './notification';
import { NotificationService } from '@app/notification.service';

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
    HomePageModule,
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
    NotificationService
  ]
})
export class AppModule {}
