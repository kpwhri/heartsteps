import { NgModule } from '@angular/core';
import { IonicStorageModule } from '@ionic/storage';
import { HeartstepsServer } from './heartsteps-server.service';
import { AuthorizationService } from './authorization.service';
import { LoadingService } from './loading.service';
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
import { AlertDialogController } from './alert-dialog.controller';
import { IonicPageModule } from 'ionic-angular';
import { HeartstepsRangeComponent } from './range.component';
import { HeartstepsIncrementComponent } from './increment.component';
import { BrowserModule } from '@angular/platform-browser';
import { NotificationService } from './notification.service';
import { DocumentStorageService } from './document-storage.service';


@NgModule({
  declarations: [
    HeartstepsRangeComponent,
    HeartstepsIncrementComponent
  ],
  imports: [
    BrowserModule,
    IonicStorageModule.forRoot(),
    IonicPageModule.forChild(HeartstepsRangeComponent)
  ],
  entryComponents: [],
  providers: [
      AuthorizationService,
      PushService,
      HeartstepsServer,
      LoadingService,
      Geolocation,
      BackgroundProcessService,
      LocationService,
      StorageService,
      DocumentStorageService,
      BrowserService,
      SafariViewController,
      InAppBrowser,
      OneSignal,
      ChoiceDialogController,
      AlertDialogController,
      NotificationService
  ],
  exports: [
    HeartstepsRangeComponent,
    HeartstepsIncrementComponent
  ]
})
export class InfrastructureModule {}
