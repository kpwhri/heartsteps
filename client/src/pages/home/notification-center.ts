import { Component, OnInit } from "@angular/core";
import { NotificationCenterService } from "@heartsteps/notification-center/notification-center.service";
import { Notification } from "@heartsteps/notification-center/Notification";

@Component({
    selector: "page-notification-center",
    templateUrl: "notification-center.html",
})
export class NotificationCenterPage implements OnInit {
    public notifications: Notification[] = [];

    constructor(private notificationService: NotificationCenterService) {
        this.notifications;
    }

    private getNotifications(): Promise<Notification[]> {
        return this.notificationService
            .getRecentNotifications()
            .then((notifications) => {
                return (this.notifications = notifications);
            });
    }

    ngOnInit() {
        this.getNotifications();
    }
}
