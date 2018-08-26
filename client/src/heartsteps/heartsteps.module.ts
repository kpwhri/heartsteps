import { NgModule } from '@angular/core';

import { HeartstepsNotifications } from './heartsteps-notifications.service';
import { InfrastructureModule } from '../infrastructure/infrastructure.module';
import { ParticipantService } from './participant.service';
import { ActivitySuggestionTimeService } from './activity-suggestion-time.service';
import { DayPlanComponent } from '@heartsteps/activity-plan/day-plan.component';
import { ActivityPlanFactory } from '@heartsteps/activity-plan/activity-plan.factory';
import { LocationModule } from '@heartsteps/location/location.module';

@NgModule({
  declarations: [
    DayPlanComponent
  ],
  imports: [
    InfrastructureModule,
    LocationModule
  ],
  providers: [
      HeartstepsNotifications,
      ParticipantService,
      ActivitySuggestionTimeService,
      ActivityPlanFactory
  ],
  exports: [
    DayPlanComponent
  ]
})
export class HeartstepsModule {}
