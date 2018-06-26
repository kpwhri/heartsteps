import { NgModule } from '@angular/core';
// import {AngularFireModule} from 'angularfire2';

import { IonicStorageModule } from '@ionic/storage';
import { AuthorizationService } from './authorization.service';
import { HeartstepsServer } from './heartsteps-server.service';
import { FcmService } from './fcm';

@NgModule({
  declarations: [
  ],
  imports: [
    IonicStorageModule.forRoot()
  ],
  entryComponents: [],
  providers: [
      AuthorizationService,
      HeartstepsServer,
      FcmService
  ]
})
export class HeartstepsModule {}
