import { Component } from '@angular/core';
import { HeartstepsNotifications } from '../../heartsteps/heartsteps-notifications.service';
import { NavController } from 'ionic-angular';
import { loadingService } from '../../infrastructure/loading.service';

@Component({
    selector: 'notifications-page',
    templateUrl: 'notifications.html',
})
export class NotificationsPage {

    constructor(
        private navCtrl:NavController,
        private heartstepsNotifications:HeartstepsNotifications,
        private loadingService:loadingService
    ) {}

    getPermission() {
        this.loadingService.show("Getting permission")
        this.heartstepsNotifications.enable()
        .then(() => {
            this.loadingService.dismiss()
            this.navCtrl.pop()
        })
        .catch(() => {
            this.loadingService.dismiss()
            console.log('No permission')
        })
    }
}
