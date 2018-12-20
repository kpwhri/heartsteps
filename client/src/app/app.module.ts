import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { IonicApp, IonicModule } from 'ionic-angular';
import { SplashScreen } from '@ionic-native/splash-screen';
import { StatusBar } from '@ionic-native/status-bar';

import { MyApp } from './app.component';

import { WelcomePageModule } from '../pages/welcome/welcome.module';
import { OnboardPageModule } from '../pages/onboard/onboard.module';
import { NotificationPane } from './notification';
import { NotificationService } from '@app/notification.service';
import { BackgroundService } from '@app/background.service';
import { LocationService } from '@heartsteps/locations/location.service';
import { HomePageModule } from '@pages/home/home.module';
import { NotificationsModule } from '@heartsteps/notifications/notifications.module';

const appRoutes:Routes = [
{
    path: '',
    redirectTo: '/home/dashboard',
    pathMatch: 'full'
  }
]

@NgModule({
  declarations: [
    MyApp,
    NotificationPane
  ],
  imports: [
    WelcomePageModule,
    OnboardPageModule,
    HomePageModule,
    NotificationsModule,
    IonicModule.forRoot(MyApp),
    RouterModule.forRoot(
      appRoutes,
      {
        enableTracing: true,
        useHash: true
      }
    )
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
    BackgroundService,
    LocationService
  ]
})
export class AppModule {}
