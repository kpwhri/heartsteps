import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { loadingService } from '@infrastructure/loading.service';

@Component({
  selector: 'fitbit-app-page',
  templateUrl: 'fitbit-app.html',
})
export class FitbitAppPage {

  constructor(
    private navCtrl:NavController,
    private loadingService:loadingService
  ) {}

  checkConnection() {
    this.loadingService.show("Checking connection")
    setTimeout(() => {
        this.loadingService.dismiss()
        this.navCtrl.pop()
    }, 5000)
  }
}
