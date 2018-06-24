import { NgModule } from '@angular/core';

import { IonicStorageModule } from '@ionic/storage';
import { AuthorizationService } from './authorization.service';
import { HeartstepsServer } from './heartsteps-server.service';

@NgModule({
  declarations: [
  ],
  imports: [
    IonicStorageModule.forRoot()
  ],
  entryComponents: [],
  providers: [
      AuthorizationService,
      HeartstepsServer
  ]
})
export class HeartstepsModule {}
