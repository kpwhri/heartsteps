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
        this.watchDeviceUpdate();
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
        return this.pushService.getPermission()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.reject("Notifications not enabled");
        })
    }

    watchDeviceUpdate() {
        this.pushService.device.subscribe((device: Device) => {
            if(device) {
                this.updateDevice(device);
            }
        })
    }

    updateDevice(device: Device):Promise<boolean> {
        console.log("sending device to heartsteps...")
        return this.heartstepsServer.post('messages/device', {
            token: device.token,
            type: device.type
        })
        .then(() => {
            console.log("device update sent");
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