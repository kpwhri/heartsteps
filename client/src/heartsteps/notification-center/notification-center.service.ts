import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { BehaviorSubject } from "rxjs";
import { Message } from "@heartsteps/notifications/message.model";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";
import { NotificationService } from "@app/notification.service";

@Injectable()
export class NotificationCenterService {
    private notifications: BehaviorSubject<Message[]> = new BehaviorSubject([]);
    public currentNotifications = this.notifications.asObservable();

    private unreadStatus: BehaviorSubject<boolean> = new BehaviorSubject(true);
    public currentUnreadStatus = this.unreadStatus.asObservable();
    public notificationRefreshInterval: any;

    constructor(
        private heartstepsServer: HeartstepsServer,
        private messageReceiptService: MessageReceiptService,
        private notificationService: NotificationService
    ) {
        this.getNotifications();
        this.notificationService.setup();
        this.notificationRefreshInterval = setInterval(() => {
            this.getNotifications();
        }, 5000);
    }

    // pull notifications from django
    public getRecentNotifications(): Promise<any> {
        return this.heartstepsServer.get("/notification_center/", {});
    }

    // re-initialize this.notifications and returns current notifications in array
    public getNotifications(): Message[] {
        this.getRecentNotifications().then((data) => {
            // console.log("unread status from API: ", data[0]);
            // console.log("notifications from API: ", data[1]);
            let newStatus = data[0];
            let res = data[1];
            let notifications: Message[] = res.map(
                this.deserializeMessage,
                this
            );
            // console.log("notifications: ", notifications);
            this.notifications.next(notifications);
            this.unreadStatus.next(newStatus);
            // console.log("this.unreadStatus: ", this.unreadStatus.value);
        });
        return this.notifications.value;
    }

    public deserializeMessage(data: any): Message {
        const message = new Message(this.messageReceiptService);
        message.id = data.uuid;
        message.type = data.type;
        message.created = data.created;
        message.title = data.title;
        message.body = data.body;
        message.sent = data.sent;
        message.received = data.received;
        message.opened = data.opened;
        message.engaged = data.engaged;
        if (data.context) {
            message.context = data.context;
        }
        return message;
    }

    // mark a single notification as engaged (ignored)
    private updateNotification(notification: Message) {
        notification.toggleEngaged();
    }

    // redirects notification based on notification.type
    public redirectNotification(notification: Message) {
        notification.toggleOpened();
        return this.notificationService.processOpenedMessage(notification);
    }

    // mark all notifications as engaged (ignored)
    public updateAllNotifications() {
        if (this.notifications.value.length > 0) {
            this.notifications.value.map(this.updateNotification, this);
        }
    }

    // mark the first notification as engaged (ignored)
    public testUpdateNotification() {
        if (this.notifications.value.length > 0) {
            this.updateNotification(this.notifications.value[0]);
        }
    }

    // checks to see if user has seen the push notification
    public isRead(notification: Message): boolean {
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

    // checks to see if user received a push notification
    public isReceived(notification: Message): boolean {
        if (notification.sent && notification.received) {
            return true;
        }
        return false;
    }
}
