import { Component, OnInit } from "@angular/core";
import { NotificationCenterService } from "@heartsteps/notification-center/notification-center.service";
import { Notification } from "@pages/notification-center/Notification";
import { IonicPage } from "ionic-angular";

/**
 * Generated class for the NotificationCenterPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
    selector: "page-notification-center",
    templateUrl: "notification-center.html",
})
export class NotificationCenterPage implements OnInit {
    //   constructor(public navCtrl: NavController, public navParams: NavParams) {
    //   }

    public notifications: Notification[] = [];
    // TODO: remove hardocode
    private cohortId: number = 12345;
    private userId: string = "garbage";

    constructor(private notificationService: NotificationCenterService) {
        this.notifications;
    }

    ionViewDidLoad() {
        console.log("ionViewDidLoad NotificationCenterPage");
    }

    private getNotifications() {
        return this.notificationService
            .getRecentNotifications(this.cohortId, this.userId)
            .then((notifications) => {
                let stringJSON = JSON.stringify(notifications);
                // this.notifications = JSON.parse(stringJSON);
                let jsonObject = JSON.parse(stringJSON);
                this.notifications = <Notification[]>jsonObject;
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
