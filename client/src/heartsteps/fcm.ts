import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { Firebase as FirebaseNative } from '@ionic-native/firebase';
import firebase from 'firebase/app';
import 'firebase/messaging';
import { Observable } from "rxjs/Observable";
import { Observer } from "rxjs/Observer";

declare var process: {
    env: {
        FIREBASE_MESSAGING_SENDER_ID: string
    }
}

@Injectable()
export class FcmService {

    private messaging:any;
    private firebase: FirebaseNative;

    private messageObserver:Observer<any>;
    private messageObservable:Observable<any>;

    constructor(
        private platform: Platform
    ) {
        this.messageObservable = Observable.create(obs => {
            this.messageObserver = obs;
        });

        if(this.platform.is('ios') || this.platform.is('android')) {
            this.setupNative();
        } else {
            this.setupWeb();
        }
    }

    onMessage():Observable<any> {
        return this.messageObservable;
    }

    private directMessage(message:any) {
        this.messageObserver.next(message);
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
            console.log('No permissions implemented for iOS');
            return Promise.reject(false);
        }

        if(this.platform.is('android')) {
            return Promise.resolve(true);
        }

        return this.messaging.requestPermission();
    }

    getToken():Promise<string> {

        if(this.platform.is('ios') || this.platform.is('android')) {
            return this.firebase.getToken();
        }

        return this.messaging.getToken();
    }

    private setupWeb() {
        firebase.initializeApp({
            messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID
        });
        this.messaging = firebase.messaging();
        this.messaging.onMessage((data:any) => {
            if(data.notification){
                // should merge notification object into data object
                // to match cordova implementation
                this.directMessage(data.notification);
            } else {
                this.directMessage(data);
            }
            
        });
    }

    private setupNative() {
        this.firebase = new FirebaseNative();
        this.firebase.onNotificationOpen().subscribe((data) => {
            this.directMessage(data);
        });
    }
}