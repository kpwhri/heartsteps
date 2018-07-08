import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { OnboardPage } from './onboard';
import { NotificationsPage } from './notifications';
import { LocationPermissionPane } from './location-permission';
import { OnboardEndPane } from './onboard-end';

@NgModule({
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
    IonicPageModule.forChild(OnboardPage)
  ],
})
export class OnboardPageModule {}
