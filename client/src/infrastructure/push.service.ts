import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { Subject } from "rxjs/Subject";
import { BehaviorSubject } from 'rxjs';
import { OneSignal, OSNotification, OSNotificationOpenedResult } from '@ionic-native/onesignal';

declare var process: {
    env: {
        FCM_SENDER_ID: string,
        ONESIGNAL_APP_ID: string
    }
}

const firebaseId: string = process.env.FCM_SENDER_ID;
const oneSignalAppId: string = process.env.ONESIGNAL_APP_ID;

export class Device {

    public token: string;
    public type: string;

    constructor(token: string, type: string) {
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
        private platform: Platform
    ) {
        this.device = new BehaviorSubject(null);
        this.message = new Subject();

        this.platform.ready()
        .then(() => {
            this.oneSignal.setLogLevel({
                logLevel: 4,
                visualLevel: 0
            });
            return this.setup();
        });
    }

    getPermission(): Promise<boolean> {
        return this.oneSignal.promptForPushNotificationsWithUserResponse()
        .then((value) => {
            if(value) {
                return this.updatePermissions();
            } else {
                return Promise.reject("No permission granted");
            }
        })
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.reject("No permission granted");
        });
    }

    setup(): Promise<boolean> {
        return new Promise((resolve) => {
            this.oneSignal.startInit(oneSignalAppId, firebaseId);
            this.oneSignal.iOSSettings({
                kOSSettingsKeyAutoPrompt: false,
                kOSSettingsKeyInAppLaunchURL: false
            });
            this.oneSignal.inFocusDisplaying(this.oneSignal.OSInFocusDisplayOption.None);
            this.oneSignal.handleNotificationReceived().subscribe((data: OSNotification) => {
                console.log("Got a notification!!");
                this.handleNotification(data.payload);
            });
            this.oneSignal.handleNotificationOpened().subscribe((data: OSNotificationOpenedResult) => {
                console.log("Got opened notification");
                this.handleNotification(data.notification.payload);
            });
            this.oneSignal.addPermissionObserver().subscribe((data: any) => {
                console.log("Permission Changed!");
                this.updatePermissions();
            });
            this.oneSignal.endInit();

            resolve(true);
        })
    }

    updatePermissions(): Promise<Device> {
        return this.oneSignal.getIds().then((data: any) => {
            const device = new Device(
                data.userId,
                'onesignal'
            );
            this.device.next(device);
            return device;
        });
    }

    handleNotification(data: any) {
        let messageId: string;
        if (data.additionalData && data.additionalData.messageId) {
            messageId = data.additionalData.messageId;
            delete data.additionalData.messageId;
        }
        this.message.next({
            title: data.title,
            body: data.body,
            data: data.additionalData,
            messageId: messageId
        });
    }
}
