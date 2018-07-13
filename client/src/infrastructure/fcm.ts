import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { Firebase as FirebaseNative } from '@ionic-native/firebase';
import firebase from 'firebase/app';
import 'firebase/messaging';
import { Observable } from "rxjs/Observable";
import { Subject } from "rxjs/Subject";

declare var process: {
    env: {
        FIREBASE_MESSAGING_SENDER_ID: string
    }
}

@Injectable()
export class FcmService {

    private firebaseMessaging:any;
    private firebase: FirebaseNative;

    private messageSubject:Subject<any>;
    private dataSubject:Subject<any>;

    private subscriptionSetup:boolean;

    constructor(
        private platform: Platform
    ) {
        this.messageSubject = new Subject();
        this.dataSubject = new Subject();

        if(this.platform.is('ios') || this.platform.is('android')) {
            this.setupNative();
        } else {
            this.setupWeb();
        }
    }

    private directMessage(message:any) {
        if(message.body && message.title) {
            this.messageSubject.next(message);
        } else {
            this.dataSubject.next(message);
        }
    }

    onMessage():Observable<any> {
        return this.messageSubject.asObservable();
    }

    onData():Observable<any> {
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
            console.log('No permissions implemented for iOS');
            return Promise.reject(false);
        }

        if(this.platform.is('android')) {
            return Promise.resolve(true);
        }

        return this.firebaseMessaging.requestPermission();
    }

    getToken():Promise<string> {
        return this.getTokenWrapper()
        .then((token) => {
            if(!this.subscriptionSetup) {
                this.setupSubscription();
            }
            return token;
        });
    }

    private getTokenWrapper():Promise<string> {
        if(this.platform.is('ios') || this.platform.is('android')) {
            return this.firebase.getToken();
        } else {
            return this.firebaseMessaging.getToken();
        }
    }

    private setupSubscription() {
        if(this.platform.is('ios') || this.platform.is('android')) {
            this.firebase.onNotificationOpen().subscribe((data) => {
                this.directMessage(data);
            });
            this.subscriptionSetup = true;
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
            this.subscriptionSetup = true;
        }
    }

    private setupWeb() {
        firebase.initializeApp({
            messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID
        });
        this.firebaseMessaging = firebase.messaging();
        this.setupSubscription();
    }

    private setupNative() {
        this.firebase = new FirebaseNative();

        // iOS will throw error if subscription set up
        // before permission has been granted...
        if(this.platform.is('ios') && this.firebase.hasPermission()) {
            this.setupSubscription();
        } else {
            this.setupSubscription();
        }
    }
}