import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ActivitySuggestionTimes } from './activity-suggestion-times';
import { ParticipantInformationPage } from '@pages/settings/participant-information';
import { PlacesPageModule } from '@pages/places/places.module';
import { WeeklyReflectionTimePage } from '@pages/settings/weekly-reflection-time.page';

@NgModule({
  declarations: [
    ActivitySuggestionTimes,
    ParticipantInformationPage,
    WeeklyReflectionTimePage
  ],
  entryComponents: [
    ActivitySuggestionTimes,
    ParticipantInformationPage
  ],
  imports: [
    PlacesPageModule,
    IonicPageModule.forChild(WeeklyReflectionTimePage),
    IonicPageModule.forChild(ActivitySuggestionTimes),
    IonicPageModule.forChild(ParticipantInformationPage)
  ],
})
export class SettingsPageModule {}
