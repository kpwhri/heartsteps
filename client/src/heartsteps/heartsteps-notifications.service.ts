import { Injectable } from '@angular/core';
import { FcmService } from '../infrastructure/fcm';
import { HeartstepsServer } from '../infrastructure/heartsteps-server.service';
import { Observable } from 'rxjs/Observable';
import { Storage } from '@ionic/storage';

@Injectable()
export class HeartstepsNotifications {

    constructor(
        private fcmService:FcmService,
        private heartstepsServer:HeartstepsServer,
        private storage:Storage
    ){}

    enable():Promise<boolean> {
        return this.fcmService.getPermission()
        .then(() => {
            return this.fcmService.getToken()
        })
        .then(token => {
            return this.updateToken(token)
        })
        .then(() => {
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.reject(false);
        })
    }

    updateToken(token:string):Promise<boolean> {
        return this.storage.get('fcm-token')
        .then((storedToken) => {
            if(storedToken === token) {
                // Don't update token, but behave like it was updated...
                return Promise.resolve(true);
            } else {
                return this.heartstepsServer.post('device', {
                    registration_id: token,
                    type: this.fcmService.getDeviceType()
                })
            }
        })
        .then(() => {
            return this.storage.set('fcm-token', token)
        })
        .then(() => {
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    onMessage():Observable<any> {
        return this.fcmService.onMessage();
    }

    onDataMessage():Observable<any> {
        return this.fcmService.onDataMessage();
    }
}