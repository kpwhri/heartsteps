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
            'messagingSenderId': '968991210692'
        });
        this.messaging = firebase.messaging();
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
                console.log(token);
                return this.saveToken(token);
            })
            .then(() => {
                resolve(true);
            })
            .catch(() => {
                reject(false);
            });
        });
    }

    saveToken(token) {
        this.heartstepsServer.http.post('/firebaseToken', {
            token: token
        })
        .then(() => {
            console.log("updated token");
        })
        .catch(() => {
            console.log("error");
        })
    }

}