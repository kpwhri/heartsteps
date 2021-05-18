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
    private initialized: BehaviorSubject<boolean> = new BehaviorSubject(undefined);

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
        if(this.platform.is('cordova')) {
            this.ready.next(true);
            return this.hasPermission()
            .then(() => {
                return this.getDevice()
                .then((device) => {
                    this.device.next(device);
                    return true;
                });
            })
            .then(() => {
                return this.isInitialized();
            })
            .catch(() => {
                return Promise.resolve(true);
            });

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

    private isInitialized(): Promise<boolean> {
        return new Promise((resolve) => {
            this.initialized
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
        return this.isPhone()
        .then(() => {
            return this.hasProvidedPrivacyConsent()
        })
        .then(() => {
            return this.hasDevicePermission();
        });
    }

    public getPermission(): Promise<boolean> {
        console.log('PushNotificationService: Get permission');
        return this.isPhone()
        .then(() => {
            window.plugins.OneSignal.provideUserConsent(true);
            if(this.platform.is('ios')) {
                return this.getPermissionIOS();
            } else {
                return Promise.resolve(true);
            }
        });
    }

    private isPhone(): Promise<void> {
        if(this.platform.is('cordova')) {
            return Promise.resolve(undefined);
        } else {
            return Promise.reject('Not a phone');
        }
    }

    private getPermissionIOS(): Promise<boolean> {
        console.log('PushNotificationService: Get permission for iOS');
        return new Promise((resolve, reject) => {
            window.plugins.OneSignal.promptForPushNotificationsWithUserResponse(function(accepted) {
                if (accepted) {
                    console.log('got permission');
                    resolve(true)
                } else {
                    reject('Permission not accepted');
                }
            });
        });
    }

    public getDevice(): Promise<Device> {
        console.log('PushNotificaionService: get device');
        return this.getDeviceFromOneSignal()
        .then((device) => {
            return Promise.resolve(device);
        })
        .catch(() => {
            return this.waitForDevice();
        });
    }

    private waitForDevice(): Promise<Device> {
        console.log('PushNotificationService: Waiting for device token')
        return new Promise((resolve) => {
            const subscription = this.device
            .subscribe((device) => {
                if(device && device.token) {
                    subscription.unsubscribe();
                    resolve(device);
                }
            });
    
            const intervalId = setInterval(() => {
                console.log('Checking for device');
                this.getDeviceFromOneSignal()
                .then((device) => {
                    console.log('Got device');
                    clearInterval(intervalId);
                    this.device.next(device);
                })
                .catch(() => {
                    console.log('No device yet');
                });
            }, 1000)
        });
    }

    private getDeviceFromOneSignal(): Promise<Device> {
        return new Promise((resolve, reject) => {
            window.plugins.OneSignal.getPermissionSubscriptionState((status) => {
                console.log(status)
                const token = status.subscriptionStatus.userId;
                if(token) {
                    console.log('PushNotificationService: Got token ' + token);
                    const device = new Device(
                        token,
                        process.env.PUSH_NOTIFICATION_DEVICE_TYPE
                    );
                    resolve(device);
                } else {
                    reject('device not available');
                }
            });
        });
    }

    private initialize() {
        if(this.platform.is('cordova')) {
            window.plugins.OneSignal.addSubscriptionObserver(() => {
                this.zone.run(() => {
                    this.handleOneSignalSubscription();
                });
            });
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
            this.initialized.next(true);
        } else {
            this.initialized.next(true);
            console.log('Initialized!');
        }
    }

    private handleOneSignalSubscription() {
        console.log('PushNotificationService: handle OneSignal Subscription');
        this.isReady()
        .then(() => {
            window.plugins.OneSignal.getPermissionSubscriptionState((status) => {
                console.log('PushNotificationService: check permission state');
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
