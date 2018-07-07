import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import { Firebase as FirebaseNative } from '@ionic-native/firebase';
import firebase from 'firebase/app';
import 'firebase/messaging';
import { HeartstepsServer } from "./heartsteps-server.service";
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

    constructor(
        private platform: Platform,
        private heartstepsServer: HeartstepsServer
    ) {
        if(this.platform.is('ios') || this.platform.is('android')) {
            this.firebase = new FirebaseNative();
            this.firebase.onNotificationOpen().subscribe((data) => {
                console.log(data);
            });
        } else {
            firebase.initializeApp({
                messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID
            });
            this.messaging = firebase.messaging();
            this.messaging.onMessage((data:any) => {
                if(data.notification.body){
                    this.messageObserver.next(data.notification.body);
                }
            });
        }
    }

    onMessage():Observable<any> {
        return Observable.create((obs) => {
            this.messageObserver = obs;
        });
    }

    getPermission():Promise<boolean> {
        if(this.platform.is('ios')) {
            console.log('No permissions implemented for iOS');
            return Promise.reject(false);
        }

        if(this.platform.is('android')) {
            return this.firebase.getToken().then((token) => {
                return this.saveToken(token, 'android')
            })
            .then(() => {
                return Promise.resolve(true);
            })
            .catch(() => {
                return Promise.reject(false);
            });
        }

        return this.getPermissionWeb();
    }

    getPermissionWeb():Promise<boolean> {
        return this.messaging.requestPermission()
        .then(() => {
            return this.messaging.getToken();
        })
        .then((token) => {
            return this.saveToken(token, 'web');
        })
        .then(() => {
            Promise.resolve(true);
        })
        .catch(() => {
            Promise.reject(false);
        });
    }

    saveToken(token:string, deviceType:string):Promise<boolean> {
        return this.heartstepsServer.http.post('device', {
            registration: token,
            device_type: deviceType
        })
        .then(() => {
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.reject(false);
        })
    }

}