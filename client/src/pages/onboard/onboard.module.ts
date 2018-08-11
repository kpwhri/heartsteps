import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { OnboardPage } from './onboard';
import { NotificationsPage } from './notifications';
import { LocationPermissionPane } from './location-permission';
import { OnboardEndPane } from './onboard-end';
import { Geolocation } from '@ionic-native/geolocation';
import { ActivitySuggestionTimes } from './activity-suggestion-times';
import { LocationsPage } from './locations';
import { LocationEdit } from './location-edit';

@NgModule({
  providers: [
    Geolocation
  ],
  declarations: [
    OnboardPage,
    NotificationsPage,
    LocationPermissionPane,
    ActivitySuggestionTimes,
    LocationsPage,
    LocationEdit,
    OnboardEndPane
  ],
  entryComponents: [
    NotificationsPage,
    LocationPermissionPane,
    ActivitySuggestionTimes,
    LocationsPage,
    LocationEdit,
    OnboardEndPane
  ],
  imports: [
    IonicPageModule.forChild(OnboardPage),
    IonicPageModule.forChild(NotificationsPage),
    IonicPageModule.forChild(LocationPermissionPane),
    IonicPageModule.forChild(LocationsPage)
  ],
})
export class OnboardPageModule {}
