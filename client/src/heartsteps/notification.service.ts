import { Injectable } from '@angular/core';
import { HeartstepsServer } from '../infrastructure/heartsteps-server.service';
import { Observable } from 'rxjs/Observable';
import { PushService } from '@infrastructure/push.service';

@Injectable()
export class NotificationService {

    constructor(
        private pushService: PushService,
        private heartstepsServer:HeartstepsServer
    ){
        // this.onMessage().subscribe((message:any) => {
        //     this.logMessage(message.messageId, 'recieved')
        // })

        // this.onDataMessage().subscribe((data:any) => {
        //     this.logMessage(data.messageId, 'recieved')
        // })
    }

    logMessage(messageId:string, type:string) {
        this.heartstepsServer.post('messages/recieved', {
            message: messageId,
            type: type,
            time: new Date().toISOString()
        })
    }

    isEnabled():Promise<boolean> {
        // return this.fcmService.isEnabled()
        return Promise.reject("Not implemented");
    }

    enable():Promise<boolean> {
        this.pushService.setup();
        return Promise.reject("Meow!")
    }

    updateToken(token:string):Promise<boolean> {
        return this.heartstepsServer.post('messages/device', {
            token: token,
            // type: this.fcmService.getDeviceType()
        })
        .then(() => {
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        })
    }

    onMessage():Observable<any> {
        return new Observable();
        // return this.fcmService.onMessage();
    }

    onDataMessage():Observable<any> {
        return new Observable();
        // return this.fcmService.onDataMessage();
    }
}