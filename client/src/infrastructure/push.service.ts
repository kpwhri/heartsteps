import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { Subject } from "rxjs/Subject";
import { Storage } from '@ionic/storage';
import {BehaviorSubject, Subscription} from 'rxjs';
import { OneSignal, OSNotification, OSNotificationOpenedResult, OSPermissionSubscriptionState } from '@ionic-native/onesignal';

declare var process: {
    env: {
        FIREBASE_MESSAGING_SENDER_ID: string,
        ONE_SIGNAL_APP_ID: string
    }
}

const firebaseId: string = process.env.FIREBASE_MESSAGING_SENDER_ID;
const oneSignalAppId: string = process.env.ONE_SIGNAL_APP_ID;
const storageKey: string = 'fcm-token';

export class Device {

    public oneSignalId: string;
    public token: string;
    public type: string;

    constructor(oneSignalId: string, token: string, type: string) {
        this.oneSignalId = oneSignalId;
        this.token = token;
        this.type = type;
    }
}

@Injectable()
export class PushService {
    public device: BehaviorSubject<Device|null>;
    public message: Subject<any>;

    constructor(
        private oneSignal: OneSignal,
        private platform: Platform,
        private storage: Storage
    ) {
        this.device = new BehaviorSubject(null);

        this.platform.ready()
        .then(() => {
            return this.getDevice()
        })
        .then((device) => {
            this.device.next(device);
        })
        .then(() => {
            console.log("Set up onesignal");
            this.oneSignal.setLogLevel({
                logLevel: 4,
                visualLevel: 1
            });
            return this.setup();
        });
    }

    getPermission(): Promise<boolean> {
        return this.oneSignal.promptForPushNotificationsWithUserResponse()
        .then((value) => {
            if(value) {
                return Promise.resolve(true);
            } else {
                return Promise.reject("No permission granted");
            }
        });
    }

    setup(): Promise<boolean> {
        return new Promise((resolve) => {
            console.log("Firebase Id: " + firebaseId);
            console.log("AppId: " + oneSignalAppId);
            this.oneSignal.startInit(oneSignalAppId, firebaseId);
            this.oneSignal.iOSSettings({
                kOSSettingsKeyAutoPrompt: false,
                kOSSettingsKeyInAppLaunchURL: false
            });
            this.oneSignal.handleNotificationReceived().subscribe((data: OSNotification) => {
                console.log("Got a notification!!");
                this.handleNotification(data);
            })
            this.oneSignal.handleNotificationOpened().subscribe((data: OSNotificationOpenedResult) => {
                console.log("Got opened notification");
                this.handleNotification(data);
            })
            this.oneSignal.addPermissionObserver().subscribe((data: any) => {
                console.log("Permission Changed!");
                this.updatePermissions();
            })

            this.oneSignal.endInit();

            resolve(true);
        })
    }

    updatePermissions() {
        this.oneSignal.getIds().then((data: any) => {
            const device = new Device(
                data.userId,
                data.pushToken,
                'ios'
            );
            this.saveDevice(device);
        });
    }

    getDevice(): Promise<Device> {
        return this.storage.get(storageKey)
        .then((data: any) => {
            if(!data) {
                return Promise.reject("No device");
            }
            return Promise.resolve(new Device(
                data.oneSignalId,
                data.token,
                data.string
            ));
        })
    }

    saveDevice(device: Device): Promise<boolean> {
        return this.storage.set(storageKey, {
            oneSignalId: device.oneSignalId,
            token: device.token,
            type: device.type
        });
    }

    deleteDevice(): Promise<boolean> {
        return this.storage.remove(storageKey);
    }

    private handleNotification(data: any) {
        console.log(data);
        this.message.next(data);
    }
}
