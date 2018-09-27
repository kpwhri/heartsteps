import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import firebase from 'firebase/app';
import 'firebase/messaging';
import { Observable } from "rxjs/Observable";
import { Subject } from "rxjs/Subject";
import { Storage } from '@ionic/storage';
import {BehaviorSubject, Subscription} from 'rxjs';


import { Push, PushObject, PushOptions } from '@ionic-native/push';

declare var process: {
    env: {
        FIREBASE_MESSAGING_SENDER_ID: string
    }
}

const storageKey: string = 'fcm-token'

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
    private pushObject: PushObject;

    public device: BehaviorSubject<Device>;
    public message: Subject<any>;

    constructor(
        private push: Push,
        private platform: Platform,
        private storage: Storage
    ) {
        this.platform.ready()
        .then(() => {
            return this.getDevice()    
        })
        .then((device) => {
            this.device = new BehaviorSubject(device);
        })
        .then(() => {
            return this.push.hasPermission()
        })
        .then((data) => {
            if(data.isEnabled) {
                this.setupPushObject();
                this.setupHandlers();
            } else {
                console.log("No push permission");
            }
        });
    }

    hasPermission(): Promise<boolean> {
        return new Promise((resolve, reject) => {
            this.push.hasPermission()
            .then((data: any) => {
                if(data.isEnabled) {
                    resolve(true);
                } else {
                    reject(false);
                }
            })
            .catch(() => {
                reject(false);
            })
        })
    }

    setup(): Promise<boolean> {
        return new Promise((resolve, reject) => {
            this.setupPushObject()

            const subscription:Subscription = this.pushObject.on('registration').subscribe((data) => {
                this.handleRegistration(data)
                .then(() => {
                    subscription.unsubscribe();
                    this.setupHandlers();
                    resolve(true);
                });
            });
        })
    }

    setupPushObject() {
        const options:PushOptions = {
            ios: {
                voip: true
            }
        }
        this.pushObject = this.push.init(options);
    }

    setupHandlers() {
        this.pushObject.on('registration').subscribe((data) => {
            this.handleRegistration(data);
        });
        
        this.pushObject.on('notification').subscribe((data) => {
            console.log("This is a notificattion");
            console.log(data);
            this.handleNotification(data);
        });
    }

    getDevice(): Promise<Device> {
        return new Promise((resolve, reject) => {
            this.storage.get(storageKey)
            .then((data: any) => {
                if(data) {
                    const device = new Device(data.token, data.type);
                    resolve(device);
                } else {
                    reject();
                }
            })
            .catch(() => {
                reject();
            })
        });
    }

    private handleRegistration(data: any): Promise<boolean> {
        const newDevice:Device = new Device(
            data.registrationId,
            data.registrationType
        );
        return new Promise((resolve) => {
            this.getDevice()
            .then((device: Device) => {
                if(newDevice.token && device.token !== newDevice.token) {
                    return this.updateDevice(newDevice);
                } else {
                    console.log("Already saved device");
                    resolve(true);
                }
            })
            .catch(() => {
                return this.updateDevice(newDevice);
            })
            .then(() => {
                return resolve(true);
            });
        });
    }

    private updateDevice(device: Device): Promise<boolean> {
        return this.storage.set(storageKey, {
            token: device.token,
            type: device.type
        })
        .then(() => {
            if(this.device) {
                this.device.next(device);
            } else {
                this.device = new BehaviorSubject(device)
            }
            return true;
        });
    }

    private handleNotification(data: any) {
        this.message.next(data);
    }
}
