import { NgModule } from '@angular/core';

import { HeartstepsNotifications } from './heartsteps-notifications.service';
import { InfrastructureModule } from '../infrastructure/infrastructure.module';
import { ParticipantService } from './participant.service';
import { ActivitySuggestionTimeService } from './activity-suggestion-time.service';
import { ActivityPlanService } from '@heartsteps/activity-plan.service';
import { PlacesService } from '@heartsteps/places.service';

@NgModule({
  imports: [
    InfrastructureModule
  ],
  providers: [
      HeartstepsNotifications,
      ParticipantService,
      ActivitySuggestionTimeService,
      ActivityPlanService,
      PlacesService
  ]
})
export class HeartstepsModule {}
