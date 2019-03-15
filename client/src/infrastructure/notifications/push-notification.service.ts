import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { BehaviorSubject, Subject, Subscription } from "rxjs";

declare var PushNotification;

declare var process: {
    env: {
        PUSH_NOTIFICATION_DEVICE_TYPE: string
    }
}

export class Device {
    public token: string;
    public type: string;

    constructor(token:string, type:string) {
        this.token = token;
        this.type = type;
    }
}

@Injectable()
export class PushNotificationService {

    private push: any;
    public device: BehaviorSubject<Device> = new BehaviorSubject(undefined);
    public notifications: Subject<any> = new Subject();

    constructor(
        private platform: Platform
    ) {}

    public getPermission():Promise<boolean> {
        return Promise.resolve(true);
    }

    public setup():Promise<boolean> {
        if(this.platform.is('ios') || this.platform.is('android')) {
            this.push = PushNotification.init({
                android: {},
                ios:{voip: "true"}
            });

            this.push.on('notification', (data:any) => {
                if(this.platform.is('ios') && data.additionalData) {
                    this.createNotification(data.additionalData);
                }
                if(this.platform.is('android')) {
                    this.createNotification(data);
                }
            })
    
            this.push.on('registration', (data:any) => {
                this.device.next(new Device(
                    data.registrationId,
                    process.env.PUSH_NOTIFICATION_DEVICE_TYPE
                ));
            });

            return new Promise((resolve) => {
                const subscription:Subscription = this.device
                .filter(device => device !== undefined)
                .subscribe(() => {
                    subscription.unsubscribe();
                    resolve(true);
                });
            });

        } else {
            this.device.next(new Device('fake-device', 'fake'));
            return Promise.resolve(true);
        }
    }

    private createNotification(data:any) {
        const customData: any = Object.assign({}, data);
        delete customData.title;
        delete customData.body;
        delete customData.messageId;
        delete customData.coldstart;
        delete customData.foreground;
        delete customData['content-available'];

        this.notifications.next({
            title: data.title,
            body: data.body,
            context: customData,
            id: data.messageId,
            type: data.type
        });
    }

}
