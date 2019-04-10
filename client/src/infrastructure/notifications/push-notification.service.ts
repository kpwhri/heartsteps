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
        PUSH_NOTIFICATION_DEVICE_TYPE: string,
        ONESIGNAL_APP_ID: string
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

    private ready: BehaviorSubject<boolean> = new BehaviorSubject(undefined);

    constructor(
        private platform: Platform,
        private zone: NgZone
    ) {
        this.platform.ready()
        .then(() => {
            this.initialize();
        });
    }

    public setup():Promise<boolean> {
        if(this.platform.is('ios') || this.platform.is('android')) {
            this.ready.next(true);
            return Promise.resolve(true);
        } else {
            this.device.next(new Device('fake-device', 'fake'));
            return Promise.resolve(true);
        }
    }

    private isReady(): Promise<boolean> {
        return new Promise((resolve) => {
            this.ready
            .filter(value => value === true)
            .first()
            .subscribe(() => {
                resolve(true);
            });
        });
    }

    private hasProvidedPrivacyConsent(): Promise<boolean> {
        return new Promise((resolve, reject) => {
            window.plugins.OneSignal.userProvidedPrivacyConsent((consented) => {
                if(consented) {
                    resolve(true);
                } else {
                    reject('No consent');
                }
            })
        })
    }

    private hasDevicePermission(): Promise<boolean> {
        return new Promise((resolve, reject) => {
            window.plugins.OneSignal.getPermissionSubscriptionState(function(status) {
                if(status.permissionStatus.hasPrompted && status.subscriptionStatus.subscribed) {
                    resolve(true);
                } else {
                    reject('Not prompted or not subscribed');
                }
            });
        });
    }

    public hasPermission(): Promise<boolean> {
        if(this.platform.is('ios') || this.platform.is('android')) {
            return this.hasProvidedPrivacyConsent()
            .then(() => {
                return this.hasDevicePermission();
            });
        } else {
            return Promise.reject('Not a phone');
        }
    }

    public getPermission(): Promise<boolean> {
        console.log('PushNotificaions: get permission')
        if(this.platform.is('ios') || this.platform.is('android')) {
            return new Promise((resolve, reject) => {
                window.plugins.OneSignal.provideUserConsent(true);
                window.plugins.OneSignal.promptForPushNotificationsWithUserResponse(function(accepted) {
                    if (accepted) {
                        console.log('got permission')
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

    public getDevice(): Promise<Device> {
        console.log('PushNotificaions: get device');
        return new Promise((resolve, reject) => {
            window.plugins.OneSignal.getPermissionSubscriptionState((status) => {
                console.log(status)
                const token = status.subscriptionStatus.userId;
                if(token) {
                    console.log('Got token: ' + token);
                    const device = new Device(
                        token,
                        process.env.PUSH_NOTIFICATION_DEVICE_TYPE
                    );
                    resolve(device);
                } else {
                    const subscription = this.device
                    .subscribe((device) => {
                        if(device && device.token) {
                            subscription.unsubscribe();
                            resolve(device);
                        }
                    });
                }
            });
        });
    }

    private initialize() {
        if(this.platform.is('ios') || this.platform.is('android')) {
            window.plugins.OneSignal.addSubscriptionObserver(() => {
                this.zone.run(() => {
                    this.handleOneSignalSubscription();
                });
            });
            console.log('initialize OneSignal');
            window.plugins.OneSignal.setRequiresUserPrivacyConsent(true);

            window.plugins.OneSignal.startInit(process.env.ONESIGNAL_APP_ID)
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
            console.log('END initialize OneSignal');
        }
    }

    private handleOneSignalSubscription() {
        this.isReady()
        .then(() => {
            window.plugins.OneSignal.getPermissionSubscriptionState((status) => {
                console.log('handleOneSignalSubscription');
                console.log(status)
                const token = status.subscriptionStatus.userId;
                if(token) {
                    this.device.next(new Device(
                        token,
                        process.env.PUSH_NOTIFICATION_DEVICE_TYPE
                    ));
                }
            });
        });
    }

    private handleNotification(data:any) {
        this.isReady()
        .then(() => {
            this.notifications.next({
                id: data.notification.payload.additionalData.messageId,
                type: data.notification.payload.additionalData.type,
                title: data.notification.payload.title,
                body: data.notification.payload.body,
                context: data.notification.payload.additionalData
            });
        });
    }

}
