import { Injectable, NgZone } from "@angular/core";
import { Platform } from "ionic-angular";
import { BehaviorSubject, Subject } from "rxjs";

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

    public device: BehaviorSubject<Device> = new BehaviorSubject(undefined);
    public notifications: Subject<any> = new Subject();

    constructor(
        private platform: Platform,
        private zone: NgZone
    ) {
        this.platform.ready()
        .then(() => {
            this.initialize();
        })
    }

    public setup():Promise<boolean> {
        if(this.platform.is('ios') || this.platform.is('android')) {
            return Promise.resolve(true);
        } else {
            this.device.next(new Device('fake-device', 'fake'));
            return Promise.resolve(true);
        }
    }

    public hasPermission(): Promise<boolean> {
        if(this.platform.is('ios') || this.platform.is('android')) {
            return new Promise((resolve, reject) => {
                window.plugins.OneSignal.getPermissionSubscriptionState(function(status) {
                    if(status.permissionStatus.hasPrompted && status.subscriptionStatus.subscribed) {
                        resolve(true);
                    } else {
                        reject('Not prompted or not subscribed');
                    }
                });
            });
        } else {
            return Promise.resolve(true);
        }
    }

    public getPermission(): Promise<boolean> {
        if(this.platform.is('ios') || this.platform.is('android')) {
            return new Promise((resolve, reject) => {
                window.plugins.OneSignal.promptForPushNotificationsWithUserResponse(function(accepted) {
                    if (accepted) {
                        resolve(true)
                    } else {
                        reject('Permission not accepted');
                    }
                });
            });
        } else {
            return Promise.resolve(true);
        }
    }

    private initialize() {
        if(this.platform.is('ios') || this.platform.is('android')) {
            window.plugins.OneSignal.addSubscriptionObserver((state) => {
                this.handleOneSignalSubscription(state.to.userId);
            });

            window.plugins.OneSignal.startInit('596839e2-59bf-4fcb-bc55-a6154b8403d8')
            .iOSSettings({
                'kOSSettingsKeyAutoPrompt': false,
                'kOSSettingsKeyInAppLaunchURL': true
            })
            .inFocusDisplaying(window.plugins.OneSignal.OSInFocusDisplayOption.Notification)
            .handleNotificationOpened((data) => {
                this.zone.run(() => {
                    this.handleNotification(data);
                });
            })
            .endInit();
        }
    }

    private handleOneSignalSubscription(token: string) {
        this.device.next(new Device(
            token,
            'onesignal'
        ))
    }

    private handleNotification(data:any) {
        console.log('Handle Notification');
        console.log(data);
        this.notifications.next({
            id: data.notification.payload.additionalData.messageId,
            type: data.notification.payload.additionalData.type,
            title: data.notification.payload.title,
            body: data.notification.payload.body,
            context: data.notification.payload.additionalData
        });
    }

}
