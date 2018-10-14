import { Component } from '@angular/core';
import { NotificationService } from '@heartsteps/notifications/notification.service';
import { NavController } from 'ionic-angular';
import { loadingService } from '../../infrastructure/loading.service';

@Component({
    selector: 'notifications-page',
    templateUrl: 'notifications.html',
})
export class NotificationsPage {

    constructor(
        private navCtrl:NavController,
        private notificationService: NotificationService,
        private loadingService:loadingService
    ) {}

    getPermission() {
        this.loadingService.show("Getting permission")
        this.notificationService.enable()
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
