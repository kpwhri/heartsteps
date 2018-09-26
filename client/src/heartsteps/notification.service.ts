import { Injectable } from '@angular/core';
import { HeartstepsServer } from '../infrastructure/heartsteps-server.service';
import { Observable } from 'rxjs/Observable';
import { PushService, Device } from '@infrastructure/push.service';

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
        return this.pushService.getDevice()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.reject("No device registered");
        })
    }

    enable():Promise<boolean> {
        console.log("start notification service setup")
        return this.pushService.setup()
        .then(() => {
            console.log("notification service: SETUP")
            this.watchDeviceUpdate();
            return true;
        })
        .catch(() => {
            console.log("Notification service rejected!")
            return Promise.reject("Meow!");
        })
    }

    watchDeviceUpdate() {
        console.log("watching device");
        this.pushService.device.subscribe((device: Device) => {
            console.log("updating device");
            this.updateDevice(device);
        })
    }

    updateDevice(device: Device):Promise<boolean> {
        return this.heartstepsServer.post('messages/device', {
            token: device.token,
            type: device.type
        })
        .then(() => {
            return Promise.resolve(true)
        })
        .catch(() => {
            return Promise.reject(false)
        });
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