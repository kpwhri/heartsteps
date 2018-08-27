import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { loadingService } from '@infrastructure/loading.service';

@Component({
  selector: 'fitbit-auth-page',
  templateUrl: 'fitbit-auth.html',
})
export class FitbitAuthPage {

  constructor(
    private navCtrl:NavController,
    private loadingService:loadingService
  ) {}

  getAuthorization() {
    this.loadingService.show("Authorizing FitBit")
    setTimeout(() => {
        this.loadingService.dismiss()
        this.navCtrl.pop()
    }, 5000)
  }
}
