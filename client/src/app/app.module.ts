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
import { DashboardModule } from '@pages/dashboard/dashboard.module';
import { LocationModule } from '@heartsteps/locations/location.module';
import { ParticipantModule } from '@heartsteps/participants/participant.module';
import { LocationService } from '@heartsteps/locations/location.service';
import { WelcomePage } from '@pages/welcome/welcome';

const appRoutes:Routes = [
  {
    path: '',
    component: WelcomePage,
    pathMatch: 'full'
  }
]

@NgModule({
  declarations: [
    MyApp,
    NotificationPane
  ],
  imports: [
    LocationModule,
    ParticipantModule,
    WelcomePageModule,
    OnboardPageModule,
    DashboardModule,
    IonicModule.forRoot(MyApp),
    RouterModule.forRoot(
      appRoutes,
      { enableTracing: true }
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
