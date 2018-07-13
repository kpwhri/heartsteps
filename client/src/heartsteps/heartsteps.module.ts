import { NgModule } from '@angular/core';

import { HeartstepsNotifications } from './heartsteps-notifications.service';
import { InfrastructureModule } from '../infrastructure/infrastructure.module';
import { ParticipantService } from './participant.service';

@NgModule({
  declarations: [
  ],
  imports: [
    InfrastructureModule
  ],
  entryComponents: [],
  providers: [
      HeartstepsNotifications,
      ParticipantService
  ]
})
export class HeartstepsModule {}
