import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ActivitySuggestionTimes } from './activity-suggestion-times';
import { LocationsPage } from './locations';

@NgModule({
  declarations: [
    ActivitySuggestionTimes,
    LocationsPage
  ],
  entryComponents: [
    ActivitySuggestionTimes,
    LocationsPage
  ],
  imports: [
    IonicPageModule.forChild(LocationsPage)
  ],
})
export class SettingsPageModule {}
