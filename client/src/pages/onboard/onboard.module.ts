import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { OnboardPage } from './onboard';
import { NotificationsPage } from './notifications';
import { LocationPermissionPane } from './location-permission';
import { OnboardEndPane } from './onboard-end';
import { Geolocation } from '@ionic-native/geolocation';

@NgModule({
  providers: [
    Geolocation
  ],
  declarations: [
    OnboardPage,
    NotificationsPage,
    LocationPermissionPane,
    OnboardEndPane
  ],
  entryComponents: [
    NotificationsPage,
    LocationPermissionPane,
    OnboardEndPane
  ],
  imports: [
    IonicPageModule.forChild(OnboardPage),
    IonicPageModule.forChild(NotificationsPage),
    IonicPageModule.forChild(LocationPermissionPane)
  ],
})
export class OnboardPageModule {}
