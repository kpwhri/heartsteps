import { NgModule } from '@angular/core';

import { HeartstepsNotifications } from './heartsteps-notifications.service';
import { InfrastructureModule } from '../infrastructure/infrastructure.module';
import { ParticipantService } from './participant.service';
import { ActivitySuggestionTimeService } from './activity-suggestion-time.service';
import { LocationService } from './location.service';
import { LocationsService } from './locations.service';

@NgModule({
  declarations: [
  ],
  imports: [
    InfrastructureModule
  ],
  entryComponents: [],
  providers: [
      HeartstepsNotifications,
      ParticipantService,
      ActivitySuggestionTimeService,
      LocationService,
      LocationsService
  ]
})
export class HeartstepsModule {}
