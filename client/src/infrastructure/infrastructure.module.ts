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
import { SafariViewController } from '@ionic-native/safari-view-controller';
import { InAppBrowser } from '@ionic-native/in-app-browser';


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
      SafariViewController,
      InAppBrowser,
      Push
  ]
})
export class InfrastructureModule {}
