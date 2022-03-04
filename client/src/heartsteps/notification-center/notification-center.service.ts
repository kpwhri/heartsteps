import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { BehaviorSubject } from "rxjs";
import { Message } from "@heartsteps/notifications/message.model";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";
import { NotificationService } from "@app/notification.service";
import { StorageService } from "@infrastructure/storage.service";

const storageKey: string = "notification-center";

@Injectable()
export class NotificationCenterService {
    private notifications: BehaviorSubject<Message[]> = new BehaviorSubject([]);
    public currentNotifications = this.notifications.asObservable();

    private unreadStatus: BehaviorSubject<boolean> = new BehaviorSubject(true);
    public currentUnreadStatus = this.unreadStatus.asObservable();

    private offlineStatus: BehaviorSubject<boolean> = new BehaviorSubject(
        false
    );
    public currentOfflineStatus = this.offlineStatus.asObservable();

    public notificationRefreshInterval: any;

    constructor(
        private heartstepsServer: HeartstepsServer,
        private messageReceiptService: MessageReceiptService,
        private notificationService: NotificationService,
        private storage: StorageService
    ) {
        this.get();
        this.refreshNotifications();
        this.notificationService.setup();
        this.notificationRefreshInterval = setInterval(() => {
            this.refreshNotifications();
        }, 4000);
    }

    // pull notifications from django
    public getRecentNotifications(): Promise<any> {
        return this.heartstepsServer.get("/notification_center/", {}, false);
    }

    // re-initialize this.notifications and returns current notifications in array
    public refreshNotifications(): Promise<Message[]> {
        // let localNotifications: Message[];
        // let areLocal: boolean = false;
        // this.storage.get(storageKey).then((data) => {
        //     localNotifications = data.map(this.deserializeMessage, this);
        //     areLocal = true;
        // });

        // TODO: DO MORE PROMISE REJECT FOR .CATCH TO SEE IF API CALL FAILS

        return this.getRecentNotifications()
            .then((data) => {
                // console.log("NC: data from django", data);
                let newStatus = data[0];
                let res = data[1];

                let notifications: Message[] = res.map(
                    this.deserializeMessage,
                    this
                );
                this.offlineStatus.next(false);
                this.notifications.next(notifications);
                this.unreadStatus.next(newStatus);
                return notifications;
            })
            .then((notifications) => {
                return this.set(notifications);
            })
            .catch(() => {
                this.offlineStatus.next(true);
                return this.loadLocalNotifications();
            });
    }

    // tries to get notifications from local storage and if fails, pull from django db
    public get(): Promise<Message[]> {
        // console.log("NC: get()");
        return this.loadLocalNotifications().catch(() => {
            // console.log("NC: catch inside get()");
            return this.refreshNotifications();
        });
    }

    // load notifications on offline local storage
    public loadLocalNotifications(): Promise<Message[]> {
        // TODO: implement unreadStatus
        // console.log("NC: loadLocalNotifcations()");
        return this.storage.get(storageKey).then((data) => {
            let notifications: Message[] = data.map(
                this.deserializeMessage,
                this
            );
            this.notifications.next(notifications);
            return notifications;
        });
    }

    // re-assign local notifications to notificationList
    public set(notificationsList: Message[]): Promise<Message[]> {
        // console.log("NC: set()");
        let serialized = this.serializeMany(notificationsList);
        return this.storage.set(storageKey, serialized).then((value) => {
            // console.log("NC: storage sucess", value);
            return value;
        });
    }

    // serialize Message[] object into generic dictionary object
    // TODO: test to make sure it works
    public serializeMany(notificationsList: Message[]) {
        return notificationsList.map(this.serializeOne, this);
    }

    public serializeOne(obj: Message) {
        if (obj.context) {
            return {
                uuid: obj.id,
                type: obj.type,
                created: obj.created,
                title: obj.title,
                body: obj.body,
                sent: obj.sent,
                received: obj.received,
                opened: obj.opened,
                engaged: obj.engaged,
                context: obj.context,
            };
        }
        return {
            uuid: obj.id,
            type: obj.type,
            created: obj.created,
            title: obj.title,
            body: obj.body,
            sent: obj.sent,
            received: obj.received,
            opened: obj.opened,
            engaged: obj.engaged,
        };
    }

    // remove notification-center key and value from local storage
    public clear(): Promise<boolean> {
        return this.storage.remove(storageKey).then(() => {
            return true;
        });
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
