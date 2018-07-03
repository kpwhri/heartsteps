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

@NgModule({
  declarations: [
    MyApp
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
    MyApp
  ],
  providers: [
    StatusBar,
    SplashScreen,
    {provide: ErrorHandler, useClass: IonicErrorHandler}
  ]
})
export class AppModule {}
