import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ActivitySuggestionTimes } from './activity-suggestion-times';
import { LocationsPage } from './locations';
import { LocationEdit } from './location-edit';

@NgModule({
  declarations: [
    ActivitySuggestionTimes,
    LocationsPage,
    LocationEdit,
  ],
  entryComponents: [
    ActivitySuggestionTimes,
    LocationsPage,
    LocationEdit,
  ],
  imports: [
    IonicPageModule.forChild(LocationsPage)
  ],
})
export class SettingsPageModule {}
