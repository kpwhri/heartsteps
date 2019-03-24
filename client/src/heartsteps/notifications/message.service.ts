import { Injectable } from '@angular/core';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';
import { Subject } from 'rxjs';
import { MessageReceiptService } from '@heartsteps/notifications/message-receipt.service';
import { StorageService } from '@infrastructure/storage.service';
import { PushNotificationService, Device } from '@infrastructure/notifications/push-notification.service';
import { DocumentStorage, DocumentStorageService } from '@infrastructure/document-storage.service';
import { Message } from './message.model';

const storageKey: string = 'notificationServiceDevice';

@Injectable()
export class MessageService {

    private messageStorage: DocumentStorage;

    public received: Subject<any> = new Subject();
    public opened: Subject<any> = new Subject();

    private isSetup: boolean = false;

    constructor(
        private pushNotificationService: PushNotificationService,
        private messageReceiptService: MessageReceiptService,
        private heartstepsServer:HeartstepsServer,
        private storage:StorageService,
        private documentStorageService: DocumentStorageService
    ) {}

    public setup():Promise<boolean> {
        if(this.isSetup) {
            return Promise.resolve(true);
        } else {
            this.isSetup = true;

            this.messageStorage = this.documentStorageService.create('heartsteps-messages');

            this.pushNotificationService.device.subscribe((device: Device) => {
                this.checkDevice(device);
            });
            this.pushNotificationService.notifications.subscribe((data: any) => {
                this.receiveMessage(data);
            });

            this.pushNotificationService.setup()
            .then(() => {
                return true;
            });
        }
    }

    private receiveMessage(payload: any) {
        console.log('MessageService: received message');
        const message:Message = this.deserializeMessage(payload);
        console.log('MessageService: deserialize message');
        this.saveMessage(message)
        .then(() => {
            console.log('MessageService: save message');
            return message.received();
        })
        .then(() => {
            console.log('MessageService: message marked received');
            this.received.next(message);
        });
    }

    public createNotification(id: string, text: string): Promise<boolean> {
        return Promise.reject('Do not create notification');
    }

    public isEnabled():Promise<boolean> {
        return this.getDevice()
        .then(() => {
            return true;
        })
        .catch(() => {
            return Promise.reject("No device registered");
        })
    }

    public enable():Promise<boolean> {
        return this.setup()
        .then(() => {
            return this.pushNotificationService.getPermission();
        })
        .then(() => {
            return this.waitForDevice();
        });
    }

    private waitForDevice():Promise<boolean> {
        return new Promise((resolve, reject) => {
            const subscription = this.pushNotificationService.device
            .filter(device => device !== undefined)
            .subscribe((device) =>  {
                this.updateDevice(device)
                .then(() => {
                    resolve(true);
                })
                .catch((error) => {
                    reject(error)
                })
                .then(() => {
                    subscription.unsubscribe();
                });
            });
        });
    }

    public disable():Promise<boolean> {
        return this.deleteDevice();
    }

    private checkDevice(device: Device) {
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
    }

    private updateDevice(device: Device):Promise<boolean> {
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

    private getDevice(): Promise<Device> {
        return this.storage.get(storageKey)
        .then((data: any) => {
            return Promise.resolve(new Device(
                data.token,
                data.string
            ));
        })
    }

    private saveDevice(device: Device): Promise<boolean> {
        return this.storage.set(storageKey, {
            token: device.token,
            type: device.type
        });
    }

    private deleteDevice(): Promise<boolean> {
        return this.storage.remove(storageKey);
    }

    public getMessage(messageId:string):Promise<Message> {
        return this.messageStorage.get(messageId)
        .then((data) => {
            return this.deserializeMessage(data);
        })
    }

    private serializeMessage(message: Message):any {
        return {
            id: message.id,
            type: message.type,
            title: message.title,
            body: message.body,
            context: Object.assign({}, message.context)
        }
    }

    private deserializeMessage(data: any): Message {
        const message = new Message(this.messageReceiptService);
        message.id = data.id;
        message.type = data.type;
        message.title = data.title;
        message.body = data.body;
        if (data.context) {
            message.context = data.context;
        }
        return message;
    }

    public saveMessage(message: Message):Promise<Message> {
        return this.messageStorage.set(
            message.id,
            this.serializeMessage(message)
        )
        .then(() => {
            return message;
        });
    }
}
