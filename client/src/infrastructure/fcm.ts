import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { Firebase as FirebaseNative } from '@ionic-native/firebase';
import firebase from 'firebase/app';
import 'firebase/messaging';
import { Observable } from "rxjs/Observable";
import { Subject } from "rxjs/Subject";
import { Storage } from '@ionic/storage';

declare var process: {
    env: {
        FIREBASE_MESSAGING_SENDER_ID: string
    }
}

const fcmTokenKey = 'fcm-token'

@Injectable()
export class FcmService {

    private firebaseMessaging:any;
    private firebase: FirebaseNative;

    private messageSubject:Subject<any>;
    private dataSubject:Subject<any>;
    constructor(
        private platform: Platform,
        private storage:Storage
    ) {
        this.messageSubject = new Subject();
        this.dataSubject = new Subject();

        if(this.platform.is('ios') || this.platform.is('android')) {
            this.setupNative();
        } else {
            this.setupWeb();
        }

        this.setupSubscription()
    }

    isEnabled():Promise<boolean> {
        return this.storage.get(fcmTokenKey)
        .then((value) => {
            if(value) {
                return Promise.resolve(true)
            } else {
                return Promise.reject(false)
            }
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    private directMessage(message:any) {
        if(message.aps && message.aps.alert) {
            this.messageSubject.next(message.aps.alert)
        }
        else if(message.body && message.title) {
            this.messageSubject.next(message);
        } else {
            this.dataSubject.next(message);
        }
    }

    onMessage():Observable<any> {
        return this.messageSubject.asObservable();
    }

    onDataMessage():Observable<any> {
        return this.dataSubject.asObservable();
    }

    getDeviceType():string {
        if(this.platform.is('ios')) {
            return 'ios';
        }
        if(this.platform.is('android')) {
            return 'android';
        }
        return 'web';
    }

    getPermission():Promise<boolean> {
        if(this.platform.is('ios')) {
            return this.firebase.grantPermission()
        }

        if(this.platform.is('android')) {
            return Promise.resolve(true);
        }

        return this.firebaseMessaging.requestPermission();
    }

    private getTokenWrapper():Promise<string> {
        if(this.platform.is('ios') || this.platform.is('android')) {
            return this.firebase.getToken();
        } else {
            return this.firebaseMessaging.getToken();
        }
    }

    getToken():Promise<string> {
        return this.getTokenWrapper()
        .then((token) => {
            return this.saveToken(token)
        })
        .then((token) => {
            this.setupSubscription()
            .catch(() => {
                console.log("no subscription")
            });
            return token
        });
    }

    saveToken(token:string):Promise<string> {
        return new Promise((resolve, reject) => {
            return this.storage.set(fcmTokenKey, token)
            .then(() => {
                resolve(token)
            })
            .catch(() => {
                reject()
            })
        })
    }

    private setupSubscription():Promise<boolean> {
        return this.storage.get(fcmTokenKey)
        .then((token) => {
            if(!token) {
                return Promise.resolve(true)
            }

            if(this.platform.is('ios') || this.platform.is('android')) {
                this.firebase.onNotificationOpen().subscribe((data) => {
                    this.directMessage(data);
                });
            } else {
               this.firebaseMessaging.onMessage((data:any) => {
                    if(data.notification){
                        // should merge notification object into data object
                        // to match cordova implementation
                        this.directMessage(data.notification);
                    } else {
                        this.directMessage(data);
                    }
                });
            }
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    private setupWeb() {
        firebase.initializeApp({
            messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID
        });
        this.firebaseMessaging = firebase.messaging();
    }

    private setupNative() {
        this.firebase = new FirebaseNative();
    }
}