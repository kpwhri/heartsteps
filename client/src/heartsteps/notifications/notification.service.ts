import { Injectable } from '@angular/core';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';
import { PushService, Device } from '@infrastructure/push.service';
import { Subject } from 'rxjs';
import { MessageReceiptService } from '@heartsteps/notifications/message-receipt.service';
import { Notification } from '@heartsteps/notifications/notification.model';
import { StorageService } from '@infrastructure/storage.service';

const storageKey: string = 'notificationServiceDevice';

@Injectable()
export class NotificationService {

    dataMessage: Subject<any>;
    notificationMessage: Subject<Notification>;

    constructor(
        private pushService: PushService,
        private messageReceiptService: MessageReceiptService,
        private heartstepsServer:HeartstepsServer,
        private storage:StorageService
    ){
        this.dataMessage = new Subject();
        this.notificationMessage = new Subject();
        
        this.watchDeviceUpdate();
        this.pushService.message.subscribe((data: any) => {
            this.processMessage(data);
        });
    }

    processMessage(data: any) {
        this.messageReceiptService.received(data.messageId)
        .then(() => {
            if(data.body) {
                this.notificationMessage.next(new Notification(data.messageId, data.title, data.body));
            }
            if(data.data) {
                this.dataMessage.next(data.data);
            }
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

    disable():Promise<boolean> {
        return this.deleteDevice();
    }

    watchDeviceUpdate() {
        this.pushService.device.subscribe((device: Device) => {
            if(device) {
                this.getDevice()
                .then((storedDevice)=> {
                    if(storedDevice.token !== device.token) {
                        return Promise.reject("Device needs to be updated");
                    }
                })
                .catch(() => {
                    this.updateDevice(device);
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