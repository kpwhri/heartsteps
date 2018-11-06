import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { OnboardPage } from './onboard';
import { OnboardEndPane } from './onboard-end';
import { NotificationsPage } from './notifications';
import { LocationPermissionPane } from './location-permission';
import { SettingsPageModule } from '../settings/settings.module';
import { PlacesPageModule } from '@pages/places/places.module';
import { FitbitAuthPage } from '@pages/onboard/fitbit-auth';
import { FitbitAppPage } from '@pages/onboard/fitbit-app';
import { ActivitySuggestionsModule } from '@heartsteps/activity-suggestions/activity-suggestions.module';

@NgModule({
  declarations: [
    NotificationsPage,
    LocationPermissionPane,
    FitbitAuthPage,
    FitbitAppPage,
    OnboardPage,
    OnboardEndPane
  ],
  entryComponents: [
    NotificationsPage,
    LocationPermissionPane,
    FitbitAuthPage,
    FitbitAppPage,
    OnboardEndPane
  ],
  imports: [
    SettingsPageModule,
    PlacesPageModule,
    ActivitySuggestionsModule,
    IonicPageModule.forChild(FitbitAppPage),
    IonicPageModule.forChild(FitbitAuthPage),
    IonicPageModule.forChild(LocationPermissionPane),
    IonicPageModule.forChild(NotificationsPage),
    IonicPageModule.forChild(OnboardPage)
  ],
})
export class OnboardPageModule {}
