import { Component, OnInit } from "@angular/core";
import { NotificationCenterService } from "@heartsteps/notification-center/notification-center.service";
import { Notification } from "@pages/notification-center/Notification";
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
export class NotificationCenterPage implements OnInit {
    //   constructor(public navCtrl: NavController, public navParams: NavParams) {
    //   }

    // TODO: change type from any
    // TODO: make private if possible
    public notifications: any = "default notification filler";
    public jsonObject: any = "default";
    public test: string = "";

    constructor(private notificationService: NotificationCenterService) {}

    //   ionViewDidLoad() {
    //     console.log('ionViewDidLoad NotificationCenterPage');
    //   }

    public getNotifications() {
        return this.notificationService
            .getRecentNotifications()
            .then((notifications) => {
                this.test = "test123";
                let stringJSON = JSON.stringify(notifications);
                // this.notifications = JSON.parse(stringJSON);
                // TODO: where is console.log going?
                // TODO: How do I debug effectively here?
                this.jsonObject = JSON.parse(stringJSON);
                this.notifications = <Notification[]>this.jsonObject;
                console.log(notifications);
            });
    }

    ngOnInit() {
        this.getNotifications();
    }

    // public getNotifications() {
    //     return this.notificationService.getRecentNotifications();
    // }
}
