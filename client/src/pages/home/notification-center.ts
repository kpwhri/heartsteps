import { Component, OnInit } from "@angular/core";
import { NotificationCenterService } from "@heartsteps/notification-center/notification-center.service";
import { Notification } from "@heartsteps/notification-center/Notification";

@Component({
    selector: "page-notification-center",
    templateUrl: "notification-center.html",
})
export class NotificationCenterPage implements OnInit {
    public notifications: Notification[] = [];
    // TODO: remove hardocode
    private cohortId: number = 12345;
    private userId: string = "garbage";

    constructor(private notificationService: NotificationCenterService) {
        this.notifications;
    }

    private getNotifications(): Promise<Notification[]> {
        return this.notificationService
            .getRecentNotifications(this.cohortId, this.userId)
            .then((notifications) => {
                return (this.notifications = notifications);
            });
    }

    ngOnInit() {
        this.getNotifications();
    }
}
