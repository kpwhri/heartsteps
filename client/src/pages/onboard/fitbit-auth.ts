import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { loadingService } from '@infrastructure/loading.service';
import { BrowserService } from '@infrastructure/browser.service';
import urljoin from 'url-join';
import { ParticipantService } from '@heartsteps/participant.service';

declare var process: {
  env: {
      HEARTSTEPS_URL: string
  }
}

@Component({
  selector: 'fitbit-auth-page',
  templateUrl: 'fitbit-auth.html',
  providers: [BrowserService]
})
export class FitbitAuthPage {

  constructor(
    private navCtrl:NavController,
    private loadingService:loadingService,
    private participantService: ParticipantService,
    private browser: BrowserService
  ) {}

  getAuthorization() {
    this.loadingService.show("Opening FitBit");
    this.participantService.getHeartstepsId()
    .then((heartstepsId) => {
      this.loadingService.show("Waiting for FitBit authorization");
      this.browser.open(urljoin(process.env.HEARTSTEPS_URL, 'fitbit/authorize', heartstepsId));
    })
  }
}
