import { Component } from '@angular/core';
import { FcmService } from '../../heartsteps/fcm';

/**
 * Generated class for the OnboardPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@Component({
  selector: 'notifications-page',
  templateUrl: 'notifications.html',
})
export class NotificationsPage {

  constructor(private fcmService:FcmService) {}

  getPermission() {
    this.fcmService.getPermission()
    .then(() => {
        console.log('Got permission');
    })
    .catch(() => {
        console.log('No permission');
    })
  }
}
