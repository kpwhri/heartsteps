import { Component } from '@angular/core';
import { HeartstepsNotifications } from '../../heartsteps/heartsteps-notifications.service';
import { NavController } from 'ionic-angular';

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

  constructor(private navCtrl:NavController, private heartstepsNotifications:HeartstepsNotifications) {}

  getPermission() {
    this.heartstepsNotifications.enable()
    .then(() => {
        console.log("got permission")
        this.navCtrl.pop();
    })
    .catch(() => {
        console.log('No permission');
    })
  }
}
