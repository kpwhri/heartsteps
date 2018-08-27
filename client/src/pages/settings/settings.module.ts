import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ActivitySuggestionTimes } from './activity-suggestion-times';
import { LocationsPage } from './locations';
import { ParticipantInformationPage } from '@pages/settings/participant-information';

@NgModule({
  declarations: [
    ActivitySuggestionTimes,
    LocationsPage,
    ParticipantInformationPage
  ],
  entryComponents: [
    ActivitySuggestionTimes,
    LocationsPage,
    ParticipantInformationPage
  ],
  imports: [
    IonicPageModule.forChild(LocationsPage),
    IonicPageModule.forChild(ActivitySuggestionTimes),
    IonicPageModule.forChild(ParticipantInformationPage)
  ],
})
export class SettingsPageModule {}
