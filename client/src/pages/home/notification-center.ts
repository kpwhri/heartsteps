import { Component, OnInit, OnDestroy } from "@angular/core";
import { NotificationCenterService } from "@heartsteps/notification-center/notification-center.service";
import { Notification } from "@heartsteps/notification-center/Notification";

@Component({
    selector: "page-notification-center",
    templateUrl: "notification-center.html",
})
export class NotificationCenterPage implements OnInit, OnDestroy {
    public notifications: Notification[] = [];

    constructor(private notificationService: NotificationCenterService) {
        this.notifications;
    }

    // pull notifications from django
    private getNotifications(): Promise<Notification[]> {
        return this.notificationService
            .getRecentNotifications()
            .then((notifications) => {
                return (this.notifications = notifications);
            });
    }

    // checks to see if user has seen the push notification
    public isRead(notification: Notification): boolean {
        if (this.isReceived(notification)) {
            /* 
            engaged means user dismissed notification from their OS notification center
            opened means user opened push notification and it launched heartsteps app 
            */
            if (notification.engaged || notification.opened) {
                return true;
            }
            return false;
        }
        return false;
    }

    // checks to see if user got a push notification
    public isReceived(notification: Notification): boolean {
        if (notification.sent && notification.received) {
            return true;
        }
        return false;
    }

    private updateReadStatus(): void {
        console.log("updating notification read status");
        for (let i = 0; i < this.notifications.length; i++) {
            console.log(this.notifications[i]);
            if (this.isReceived(this.notifications[i])) {
                // if this message is unread
                if (this.isRead(this.notifications[i]) === false) {
                    console.log("unread message num: ", i);
                    // TODO: make a post request and change to read
                } else {
                    console.log("read message num: ", i);
                }
            } else {
                console.log("unreceived message num: ", i);
            }
        }
        return;
    }

    ngOnInit() {
        this.getNotifications();
    }

    ngOnDestroy() {
        this.updateReadStatus();
    }
}
