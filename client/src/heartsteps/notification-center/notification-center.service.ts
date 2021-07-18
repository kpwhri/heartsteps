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
            this.refreshNotifications();
        }, 5000);
    }

    // pull notifications from django
    public getRecentNotifications(): Promise<Message[]> {
        return this.heartstepsServer.get("/notification_center/", {});
    }

    // re-initialize this.notifications and returns current notifications in array
    public getNotifications(): Message[] {
        this.getRecentNotifications().then((data) => {
            let notifications: Message[] = data.map(
                this.deserializeMessage,
                this
            );
            console.log("notifications: ", notifications);
            this.notifications.next(notifications);
        });
        return this.notifications.value;
    }

    public deserializeMessage(data: any): Message {
        const message = new Message(this.messageReceiptService);
        message.id = data.uuid;
        message.type = data.message_type;
        message.created = data.created;
        message.title = data.title;
        message.body = data.body;
        message.sent = data.sent;
        message.received = data.received;
        message.opened = data.opened;
        message.engaged = data.engaged;
        if (data.data) {
            message.context = data.data;
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

    // update unread status based on if there are unread notifications
    public updateUnreadStatus(): boolean {
        let newStatus: boolean = this.areUnreadNotifications();
        this.unreadStatus.next(newStatus);
        console.log("this.unreadStatus: ", this.unreadStatus.value);
        return newStatus;
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

    private areUnreadNotifications(): boolean {
        // if we have any notifications
        if (this.notifications.value.length > 0) {
            for (let i = 0; i < this.notifications.value.length; i++) {
                if (
                    this.isReceived(this.notifications.value[i]) &&
                    this.isRead(this.notifications.value[i]) === false
                ) {
                    return true;
                }
            }
        }
        // we have no notifications or no unread notifications
        return false;

        // if (this.notifications.value.length % 2 === 0) {
        //     return true;
        // }
        // return false;
        // console.log(
        //     "this.notifications.value.length: ",
        //     this.notifications.value.length
        // );
    }

    refreshNotifications() {
        this.getNotifications();
        this.updateUnreadStatus();
    }
}
