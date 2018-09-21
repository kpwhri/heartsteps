import { Injectable } from "@angular/core";
import { Platform } from "ionic-angular";
import firebase from 'firebase/app';
import 'firebase/messaging';
import { Observable } from "rxjs/Observable";
import { Subject } from "rxjs/Subject";
import { Storage } from '@ionic/storage';

import { Push, PushObject, PushOptions } from '@ionic-native/push';

declare var process: {
    env: {
        FIREBASE_MESSAGING_SENDER_ID: string
    }
}

const fcmTokenKey = 'fcm-token'

@Injectable()
export class PushService {
    private pushObject: PushObject;

    constructor(
        private push: Push,
        private platform: Platform,
        private storage: Storage
    ) {
        this.platform.ready()
        .then(() => {
            return this.push.hasPermission()
        })
        .then((data) => {
            if(data.isEnabled) {
                this.setup()
            } else {
                console.log("No push permission");
            }
        });
    }

    setup() {
        const options:PushOptions = {
            ios: {
                alert: 'true',
                badge: true,
                sound: 'false',
                fcmSandbox: true
            }
        }
        console.log("Ask for permission")
        this.pushObject = this.push.init(options);
        console.log("Do we stop here?");
        this.pushObject.on('registration').subscribe((data) => {
            console.log("Registration");
            console.log(data);
        });
        this.pushObject.on('notification').subscribe((data) => {
            console.log("This is a notificattion");
        })

    }

    private handleRegistration() {

    }

    private handleNotification() {

    }
}