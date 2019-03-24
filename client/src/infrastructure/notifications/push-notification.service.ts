import { Injectable, EventEmitter } from "@angular/core";
import { Platform } from "ionic-angular";
import { BehaviorSubject, Subject, Subscription } from "rxjs";

declare var window: {
    plugins: {
        OneSignal: any
    }
}

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

    private ready: boolean = false;
    private readyEvent: EventEmitter<boolean> = new EventEmitter();

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
            this.initialize();
            return this.isSetup()
            .then(() => {
                this.ready = true;
                this.readyEvent.emit(true);
                return true;
            });
        } else {
            this.ready = true;
            this.readyEvent.emit(true);
            this.device.next(new Device('fake-device', 'fake'));
            return Promise.resolve(true);
        }
    }

    private isReady():Promise<boolean> {
        if (this.ready) {
            return Promise.resolve(true);
        } else {
            return new Promise((resolve) => {
                const subscription = this.readyEvent.subscribe(() => {
                    this.ready = true;
                    subscription.unsubscribe();
                    resolve(true);
                });
            })
        }
    }

    private isSetup():Promise<boolean> {
        return new Promise((resolve) => {
            const subscription:Subscription = this.device
            .filter(device => device !== undefined)
            .subscribe(() => {
                subscription.unsubscribe();
                resolve(true);
            });
        });
    }

    private initialize() {
        if(this.platform.is('ios') || this.platform.is('android')) {
            window.plugins.OneSignal.startInit('596839e2-59bf-4fcb-bc55-a6154b8403d8')
            .handleNotification((data) => {
                this.handleNotification(data);
            })
            .endInit();
        }
    }

    private handleNotification(data:any) {
        console.log('Handle Notification');
        console.log(data);
    }

}
