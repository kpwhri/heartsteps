import { Injectable } from '@angular/core';
import { FcmService } from './fcm';
import { HeartstepsServer } from './heartsteps-server.service';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class HeartstepsNotifications {

    constructor(private fcmService:FcmService, private heartstepsServer:HeartstepsServer) {

    }

    enable():Promise<boolean> {
        return this.fcmService.getPermission()
        .then(() => {
            return this.fcmService.getToken()
        })
        .then(token => {
            return this.heartstepsServer.http.post('device', {
                registration: token,
                device_type: this.fcmService.getDeviceType()
            });
        })
        .then(() => {
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.reject(false);
        })
    }

    onMessage():Observable<any> {
        return this.fcmService.onMessage();
    }
}