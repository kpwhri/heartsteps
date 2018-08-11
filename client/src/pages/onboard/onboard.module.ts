import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { OnboardPage } from './onboard';
import { OnboardEndPane } from './onboard-end';
import { NotificationsPage } from './notifications';
import { LocationPermissionPane } from './location-permission';
import { SettingsPageModule } from '../settings/settings.module';

@NgModule({
  declarations: [
    NotificationsPage,
    LocationPermissionPane,
    OnboardPage,
    OnboardEndPane
  ],
  entryComponents: [
    NotificationsPage,
    LocationPermissionPane,
    OnboardEndPane
  ],
  imports: [
    SettingsPageModule,
    IonicPageModule.forChild(OnboardPage)
  ],
})
export class OnboardPageModule {}
