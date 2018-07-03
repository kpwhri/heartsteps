import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import firebase from 'firebase/app';
import 'firebase/messaging';
import { HeartstepsServer } from "./heartsteps-server.service";



@Injectable()
export class FcmService {

    messaging:any;

    constructor(
        private platform: Platform,
        private heartstepsServer: HeartstepsServer
    ) {
        firebase.initializeApp({
            apiKey: "AIzaSyAopOuROiYnX7RC_sSVhSJQIESUN0jEFVE",
            authDomain: "heartsteps-205523.firebaseapp.com",
            databaseURL: "https://heartsteps-205523.firebaseio.com",
            projectId: "heartsteps-205523",
            storageBucket: "heartsteps-205523.appspot.com",
            messagingSenderId: '968991210692'
        });
        this.messaging = firebase.messaging();
        this.messaging.onMessage((payload:any) => {
            console.log("hark a message");
            console.log(payload);
        });
    }

    getPermission():Promise<boolean> {
        if(this.platform.is('ios')) {
            console.log('is iOS');
            return Promise.reject(false);
        }

        if(this.platform.is('android')) {
            console.log('is android')
            return Promise.reject(false);
        }

        return this.getPermissionWeb();
    }

    getPermissionWeb():Promise<boolean> {
        return new Promise((resolve, reject) => {
            this.messaging.requestPermission()
            .then(() => {
                return this.messaging.getToken();
            })
            .then((token) => {
                return this.saveToken(token, 'web');
            })
            .then(() => {
                resolve(true);
            })
            .catch(() => {
                reject(false);
            });
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