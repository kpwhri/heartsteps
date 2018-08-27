import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ActivitySuggestionTimes } from './activity-suggestion-times';
import { ParticipantInformationPage } from '@pages/settings/participant-information';
import { PlacesPageModule } from '@pages/places/places.module';

@NgModule({
  declarations: [
    ActivitySuggestionTimes,
    ParticipantInformationPage
  ],
  entryComponents: [
    ActivitySuggestionTimes,
    ParticipantInformationPage
  ],
  imports: [
    PlacesPageModule,
    IonicPageModule.forChild(ActivitySuggestionTimes),
    IonicPageModule.forChild(ParticipantInformationPage)
  ],
})
export class SettingsPageModule {}
