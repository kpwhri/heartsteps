import { Injectable } from '@angular/core';
import { FcmService } from '../infrastructure/fcm';
import { HeartstepsServer } from '../infrastructure/heartsteps-server.service';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class HeartstepsNotifications {

    constructor(
        private fcmService:FcmService,
        private heartstepsServer:HeartstepsServer
    ){}

    isEnabled():Promise<boolean> {
        return this.fcmService.isEnabled()
    }

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
        return this.heartstepsServer.post('messages/device', {
            token: token,
            type: this.fcmService.getDeviceType()
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