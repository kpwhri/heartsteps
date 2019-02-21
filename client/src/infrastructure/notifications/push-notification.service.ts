import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { BehaviorSubject, Subject } from "rxjs";

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

    constructor() {}

    public getPermission():Promise<boolean> {
        return Promise.resolve(true);
    }

    public setup() {
        this.push = PushNotification.init({ios:{voip: "true"}});

        this.push.on('notification', (data:any) => {
            if(data.additionalData) {
                this.createNotification(data.additionalData);
            }
        })

        this.push.on('registration', (data:any) => {
            this.device.next(new Device(
                data.registrationId,
                process.env.PUSH_NOTIFICATION_DEVICE_TYPE
            ));
        });
    }

    private createNotification(data:any) {
        const title: string = data.title;
        const body: string = data.body;
        const messageId: string = data.messageId;

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
