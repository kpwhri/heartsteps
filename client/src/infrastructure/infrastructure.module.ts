import { NgModule } from '@angular/core';
import { IonicStorageModule } from '@ionic/storage';
import { HeartstepsServer } from './heartsteps-server.service';
import { AuthorizationService } from './authorization.service';
import { loadingService } from './loading.service';
import { Geolocation } from '@ionic-native/geolocation';
import { LocationService } from './location.service';
import { BrowserService } from '@infrastructure/browser.service';
import { PushService } from '@infrastructure/push.service';
import { SafariViewController } from '@ionic-native/safari-view-controller';
import { InAppBrowser } from '@ionic-native/in-app-browser';
import { OneSignal } from '@ionic-native/onesignal';
import { BackgroundProcessService } from '@infrastructure/background-process.service';
import { StorageService } from './storage.service';
import { ChoiceDialogController } from './choice-dialog.controler';


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
      BackgroundProcessService,
      LocationService,
      StorageService,
      BrowserService,
      SafariViewController,
      InAppBrowser,
      OneSignal,
      ChoiceDialogController
  ]
})
export class InfrastructureModule {}
