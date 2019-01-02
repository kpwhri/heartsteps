import { Injectable, NgZone } from "@angular/core";
import { StorageService } from "./storage.service";
import { Subject } from "rxjs";

declare var cordova:any;

export class Notification{
    public text:string;
    public type:string;
    public context:any;
}

@Injectable()
export class NotificationService {

    public notification:Subject<Notification>;

    constructor(
        private storage: StorageService,
        private zone: NgZone
    ){
        this.notification = new Subject();
    }

    public create(type:string, text:string, context:any):Promise<boolean> {
        return this.createNotification(text)
        .then(() => {
            return this.storage.set('notifications', {
                type: type,
                text: text,
                context: context
            })
        })
        .then(() => {
            return true;
        });
    }

    private createNotification(text):Promise<boolean> {
        try {
            cordova.plugins.notification.local.schedule({
                text: text
            })
            return Promise.resolve(true);
        } catch(error) {
            return Promise.resolve(true);
        }
    }

    public setupNotificationListener() {
        if(cordova) {
            cordova.plugins.notification.local.on('click', function(notification) {
                this.zone.run(() => {
                    this.readNotification(notification.text);
                })
            }, this);
        }
    }

    private readNotification(text:string) {
        this.getNotification(text)
        .then((notification) => {
            this.notification.next(notification);
        });
    }

    private getNotification(text:string):Promise<Notification> {
        return this.storage.get('notifications')
        .then((data) => {
            const notification = new Notification();
            notification.type = data.type;
            notification.text = data.text;
            notification.context = data.context;
            return notification;
        });
    }

}
