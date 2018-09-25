import { Component } from '@angular/core';
import { NavController } from 'ionic-angular';
import { loadingService } from '@infrastructure/loading.service';
import { FitbitService } from '@heartsteps/fitbit.service';

@Component({
    selector: 'fitbit-auth-page',
    templateUrl: 'fitbit-auth.html'
})
export class FitbitAuthPage {

    constructor(
        private navCtrl:NavController,
        private loadingService:loadingService,
        private fitbitService: FitbitService
    ) {}

    getAuthorization() {
        this.loadingService.show("Authorizing Fitbit");
        return this.fitbitService.authorize()
        .then(() => {
            this.navCtrl.pop();
        })
        .catch(() => {
            console.log("Authorization failed")
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }
}
