import { NgModule } from '@angular/core';

import { HeartstepsNotifications } from './heartsteps-notifications.service';
import { InfrastructureModule } from '../infrastructure/infrastructure.module';
import { ParticipantService } from './participant.service';
import { ActivitySuggestionTimeService } from './activity-suggestion-time.service';
import { LocationService } from './location.service';
import { LocationsService } from './locations.service';
import { DayPlanComponent } from '@heartsteps/activity-plan/day-plan.component';
import { ActivityPlanFactory } from '@heartsteps/activity-plan/activity-plan.factory';

@NgModule({
  declarations: [
    DayPlanComponent
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
      LocationsService,
      ActivityPlanFactory
  ],
  exports: [
    DayPlanComponent
  ]
})
export class HeartstepsModule {}
