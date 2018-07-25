import { Injectable } from '@angular/core';
import { FcmService } from '../infrastructure/fcm';
import { HeartstepsServer } from '../infrastructure/heartsteps-server.service';
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
            return this.heartstepsServer.post('device', {
                registration_id: token,
                type: this.fcmService.getDeviceType()
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

    onDataMessage():Observable<any> {
        return this.fcmService.onDataMessage();
    }
}