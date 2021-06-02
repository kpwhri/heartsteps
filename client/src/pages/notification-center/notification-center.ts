import { Component } from "@angular/core";
import { NotificationCenterService } from "@heartsteps/notification-center/notification-center.service";
// import { IonicPage, NavController, NavParams } from 'ionic-angular';

/**
 * Generated class for the NotificationCenterPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

// @IonicPage()
@Component({
    selector: "page-notification-center",
    templateUrl: "notification-center.html",
})
export class NotificationCenterPage {
    //   constructor(public navCtrl: NavController, public navParams: NavParams) {
    //   }

    public notifications = "default notification filler";
    public test: string = "";

    constructor(private notificationService: NotificationCenterService) {
        this.getNotifications();
    }

    // TODO: change type from any
    // TODO: make private if possible

    //   ionViewDidLoad() {
    //     console.log('ionViewDidLoad NotificationCenterPage');
    //   }

    public getNotifications() {
        return this.notificationService
            .getRecentNotifications()
            .then((notifications) => {
                this.test = "test123";
                this.notifications = notifications;
                // TODO: where is console.log going?
                // TODO: How do I debug effectively here?
                console.log(notifications);
            });
    }

    // public getNotifications() {
    //     return this.notificationService.getRecentNotifications();
    // }
}
