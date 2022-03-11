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

    constructor(token: string, type: string) {
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

    public setup(): Promise<boolean> {
        console.log("PushNotificationService", "setup()", 1);
        if (this.platform.is('cordova')) {
            console.log("PushNotificationService", "setup()", 2);
            this.ready.next(true);
            return this.hasPermission()
                .then(() => {
                    console.log("PushNotificationService", "setup()", 3);
                    return this.getDevice()
                        .then((device) => {
                            console.log("PushNotificationService", "setup()", 4);
                            this.device.next(device);
                            return true;
                        });
                })
                .then(() => {
                    console.log("PushNotificationService", "setup()", 5);
                    return this.isInitialized();
                })
                .catch(() => {
                    console.log("PushNotificationService", "setup()", 6);
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
                if (consented) {
                    resolve(true);
                } else {
                    reject('No consent');
                }
            })
        })
    }

    private hasDevicePermission(): Promise<boolean> {
        return new Promise((resolve, reject) => {
            window.plugins.OneSignal.getPermissionSubscriptionState(function (status) {
                if (status.permissionStatus.hasPrompted && status.subscriptionStatus.subscribed) {
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
        // TODO: delete for safety
        // return Promise.resolve(true);
        return this.isPhone()
            .then(() => {
                window.plugins.OneSignal.provideUserConsent(true);
                if (this.platform.is('ios')) {
                    return this.getPermissionIOS();
                } else {
                    return Promise.resolve(true);
                }
            });
    }

    private isPhone(): Promise<void> {
        if (this.platform.is('cordova')) {
            return Promise.resolve(undefined);
        } else {
            return Promise.reject('Not a phone');
        }
    }

    private getPermissionIOS(): Promise<boolean> {
        console.log('PushNotificationService: Get permission for iOS');
        return new Promise((resolve, reject) => {
            window.plugins.OneSignal.promptForPushNotificationsWithUserResponse(function (accepted) {
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
        console.log("PushNotificationService", "getDevice()", 1);
        return Promise.resolve(new Device("fake-token", "fake-type"));
        return this.getDeviceFromOneSignal()
            .then((device) => {
                console.log("PushNotificationService", "getDevice()", 2);
                return Promise.resolve(device);
            })
            .catch(() => {
                console.log("PushNotificationService", "getDevice()", 3);
                return this.waitForDevice();
            });
    }

    private waitForDevice(): Promise<Device> {
        console.log("PushNotificationService", "waitForDevice()", 1);
        return new Promise((resolve) => {
            console.log("PushNotificationService", "waitForDevice()", 2);
            const subscription = this.device
                .subscribe((device) => {
                    console.log("PushNotificationService", "waitForDevice()", 3);
                    if (device && device.token) {
                        console.log("PushNotificationService", "waitForDevice()", 4);
                        subscription.unsubscribe();
                        resolve(device);
                    }
                });

            console.log("PushNotificationService", "waitForDevice()", 5);
            const intervalId = setInterval(() => {
                console.log("PushNotificationService", "waitForDevice()", 6);
                console.log('Checking for device');
                this.getDeviceFromOneSignal()
                    .then((device) => {
                        console.log("PushNotificationService", "waitForDevice()", 7);
                        console.log('Got device');
                        clearInterval(intervalId);
                        this.device.next(device);
                    })
                    .catch(() => {
                        console.log("PushNotificationService", "waitForDevice()", 8);
                        console.log('No device yet');
                    });
            }, 1000)
        });
    }

    private getDeviceFromOneSignal(): Promise<Device> {
        console.log("PushNotificationService", "getDeviceFromOneSignal()", 1);

        return new Promise((resolve, reject) => {
            console.log("PushNotificationService", "getDeviceFromOneSignal()", 2);

            window.plugins.OneSignal.getDeviceState(function (stateChanges) {
                console.log("PushNotificationService", "getDeviceFromOneSignal()", 3);

                const hasNotificationPermission = stateChanges.hasNotificationPermission;
                const pushDisabled = stateChanges.pushDisabled;
                const subscribed = stateChanges.subscribed;
                const emailSubscribed = stateChanges.emailSubscribed;
                const smsSubscribed = stateChanges.smsSubscribed;
                const userId = stateChanges.userId;
                const pushToken = stateChanges.pushToken;

                if (userId) {
                    console.log("PushNotificationService", "getDeviceFromOneSignal()", 4);
                    console.log('PushNotificationService: Got token ' + userId);
                    const device = new Device(
                        userId,
                        process.env.PUSH_NOTIFICATION_DEVICE_TYPE
                    );
                    resolve(device);
                } else {
                    console.log("PushNotificationService", "getDeviceFromOneSignal()", 5);
                    reject('device not available');
                }
                console.log('OneSignal getDeviceState: ' + JSON.stringify(stateChanges));
            });

            // window.plugins.OneSignal.getPermissionSubscriptionState((status) => {

            //     console.log('window.plugins.OneSignal.getPermissionSubscriptionState', status)
            //     const token = status.subscriptionStatus.userId;
            //     if (token) {
            //         console.log("PushNotificationService", "getDeviceFromOneSignal()", 4);
            //         console.log('PushNotificationService: Got token ' + token);
            //         const device = new Device(
            //             token,
            //             process.env.PUSH_NOTIFICATION_DEVICE_TYPE
            //         );
            //         resolve(device);
            //     } else {
            //         console.log("PushNotificationService", "getDeviceFromOneSignal()", 5);
            //         reject('device not available');
            //     }
            // });
            console.log("PushNotificationService", "getDeviceFromOneSignal()", 6);
        });
    }

    private initialize() {
        console.log("infrastructure", "notifications", "push-notification.service.ts", "PushNotificationService", 'initialize()');
        if (this.platform.is('cordova')) {
            console.log('initialize', 'is cordova')
            console.log("PushNotificationService", "initialize()", 1);
            window.plugins.OneSignal.addSubscriptionObserver(function (state) {
                console.log("PushNotificationService", "initialize()", "addSubscriptionObserver()", JSON.stringify(state));
                if (!state.from.subscribed && state.to.subscribed) {
                    console.log("Subscribed for OneSignal push notifications!")
                    // get player ID
                    console.log("PushNotificationService", "initialize()", "addSubscriptionObserver()", state.to.userId);

                    var userId = state.to.userId;

                    if (userId) {
                        console.log("PushNotificationService", "initialize()", "addSubscriptionObserver()", 4);
                        console.log('PushNotificationService: Got token ' + userId);
                        const device = new Device(
                            userId,
                            process.env.PUSH_NOTIFICATION_DEVICE_TYPE
                        );
                    }
                }
            });

            console.log("PushNotificationService", "initialize()", 6);
            window.plugins.OneSignal.setRequiresUserPrivacyConsent(true);
            console.log("PushNotificationService", "initialize()", 7);
            console.log("PushNotificationService", "initialize()", "OneSignalAppId", process.env.ONESIGNAL_APP_ID);
            console.log("PushNotificationService", "initialize()", 8);
            window.plugins.OneSignal.setAppId(process.env.ONESIGNAL_APP_ID);
            console.log("PushNotificationService", "initialize()", 9);
            console.log("PushNotificationService", "initialize()", 10);
            window.plugins.OneSignal.setNotificationOpenedHandler((data) => {
                console.log("PushNotificationService", "initialize()", "notificationOpendCallback", 1);
                this.handleNotification(data);
            });
            console.log("PushNotificationService", "initialize()", 11);
            this.initialized.next(true);
            console.log("PushNotificationService", "initialize()", 12);
        } else {
            this.initialized.next(true);
        }
    }

    private handleOneSignalSubscription() {
        console.log('PushNotificationService: handle OneSignal Subscription');
        this.isReady()
            .then(() => {
                window.plugins.OneSignal.getPermissionSubscriptionState((stateChanges) => {
                    console.log("PushNotificationService", "handleOneSignalSubscription()", 3);

                    const hasNotificationPermission = stateChanges.hasNotificationPermission;
                    const pushDisabled = stateChanges.pushDisabled;
                    const subscribed = stateChanges.subscribed;
                    const emailSubscribed = stateChanges.emailSubscribed;
                    const smsSubscribed = stateChanges.smsSubscribed;
                    const userId = stateChanges.userId;
                    const pushToken = stateChanges.pushToken;

                    if (userId) {
                        console.log("PushNotificationService", "handleOneSignalSubscription()", 4);
                        console.log('PushNotificationService: Got token ' + userId);
                        const device = new Device(
                            userId,
                            process.env.PUSH_NOTIFICATION_DEVICE_TYPE
                        );
                    }
                    console.log('OneSignal getDeviceState: ' + JSON.stringify(stateChanges));
                }

                    // {
                    //     console.log('PushNotificationService: check permission state');
                    //     console.log(status)
                    //     const token = status.subscriptionStatus.userId;
                    //     if (token) {
                    //         this.device.next(new Device(
                    //             token,
                    //             process.env.PUSH_NOTIFICATION_DEVICE_TYPE
                    //         ));
                    //     }
                    // }

                );
            });
    }

    private handleNotification(data: any) {
        console.log("PushNotificationService", "handleNotification", JSON.stringify(data));
        this.isReady()
            .then(() => {
                this.notifications.next({
                    id: data.notification.additionalData.messageId,
                    type: data.action.type,
                    title: data.notification.title,
                    body: data.notification.body,
                    context: data.notification.additionalData
                });
            });
    }

}
