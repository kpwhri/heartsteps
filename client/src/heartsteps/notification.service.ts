import { Injectable } from '@angular/core';
import { HeartstepsServer } from '../infrastructure/heartsteps-server.service';
import { Observable } from 'rxjs/Observable';
import { PushService, Device } from '@infrastructure/push.service';
import { Storage } from "@ionic/storage";


const storageKey: string = 'notificationServiceDevice';

@Injectable()
export class NotificationService {

    constructor(
        private pushService: PushService,
        private heartstepsServer:HeartstepsServer,
        private storage:Storage
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
        return this.getDevice()
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
                this.getDevice()
                .then((storedDevice)=> {
                    if(storedDevice.token !== device.token) {
                        this.updateDevice(device);
                    }
                });
            }
        })
    }

    updateDevice(device: Device):Promise<boolean> {
        return this.heartstepsServer.post('messages/device', {
            token: device.token,
            type: device.type
        })
        .then(() => {
            console.log("device update sent");
            return this.saveDevice(device);
        })
        .then(() => {
            return Promise.resolve(true);
        })
        .catch(() => {
            return Promise.reject(false)
        });
    }

    getDevice(): Promise<Device> {
        return this.storage.get(storageKey)
        .then((data: any) => {
            if(!data) {
                return Promise.reject("No device");
            }
            return Promise.resolve(new Device(
                data.token,
                data.string
            ));
        })
    }

    saveDevice(device: Device): Promise<boolean> {
        return this.storage.set(storageKey, {
            token: device.token,
            type: device.type
        });
    }

    deleteDevice(): Promise<boolean> {
        return this.storage.remove(storageKey);
    }
}