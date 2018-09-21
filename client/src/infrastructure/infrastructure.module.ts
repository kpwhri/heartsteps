import { NgModule } from '@angular/core';
import { IonicStorageModule } from '@ionic/storage';
import { HeartstepsServer } from './heartsteps-server.service';
import { AuthorizationService } from './authorization.service';
import { loadingService } from './loading.service';
import { Geolocation } from '@ionic-native/geolocation';
import { LocationService } from './location.service';
import { BrowserService } from '@infrastructure/browser.service';
import { PushService } from '@infrastructure/push.service';
import { Push } from '@ionic-native/push';

@NgModule({
  declarations: [],
  imports: [
    IonicStorageModule.forRoot()
  ],
  entryComponents: [],
  providers: [
      AuthorizationService,
      PushService,
      HeartstepsServer,
      loadingService,
      Geolocation,
      LocationService,
      BrowserService,
      Push
  ]
})
export class InfrastructureModule {}
