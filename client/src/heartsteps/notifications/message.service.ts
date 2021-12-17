import { Injectable } from "@angular/core";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Subject } from "rxjs";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";
import { StorageService } from "@infrastructure/storage.service";
import {
    PushNotificationService,
    Device,
} from "@infrastructure/notifications/push-notification.service";
import {
    DocumentStorage,
    DocumentStorageService,
} from "@infrastructure/document-storage.service";
import { Message } from "./message.model";

const storageKey: string = "notificationServiceDevice";

@Injectable()
export class MessageService {
    private messageStorage: DocumentStorage;

    public opened: Subject<Message> = new Subject();

    private isSetup: boolean = false;

    constructor(
        private pushNotificationService: PushNotificationService,
        private messageReceiptService: MessageReceiptService,
        private heartstepsServer: HeartstepsServer,
        private storage: StorageService,
        private documentStorageService: DocumentStorageService
    ) { }

    public setup(): Promise<void> {
        if (this.isSetup) {
            return Promise.resolve(undefined);
        } else {
            this.isSetup = true;

            this.messageStorage = this.documentStorageService.create(
                "heartsteps-messages"
            );

            this.pushNotificationService.device.subscribe((device: Device) => {
                this.checkDevice(device);
            });
            this.pushNotificationService.notifications.subscribe(
                (data: any) => {
                    console.log(
                        "MessageService: Got notification id=" + data.id
                    );
                    console.log("MessageService: data=", data);
                    this.loadMessage(data.id).then((message) => {
                        console.log(message);
                        this.opened.next(message);
                    });
                }
            );

            return this.pushNotificationService.setup().then(() => {
                return undefined;
            });
        }
    }

    public waitUntilSetup(): Promise<void> {
        const _promise: Promise<void> = new Promise((resolve, reject) => {
            setTimeout(() => {
                if (this.isSetup) {
                    resolve();
                } else {
                    reject();
                }
            }, 500);
        });
        return _promise.catch(() => {
            return this.waitUntilSetup();
        });
    }

    public createNotification(id: string, text: string): Promise<boolean> {
        return Promise.reject("Do not create notification");
    }

    public requestedPermission(): Promise<boolean> {
        return this.pushNotificationService
            .hasPermission()
            .then(() => {
                return true;
            })
            .catch(() => {
                return this.storage.get("notificationsDisabled");
            })
            .then(() => {
                return true;
            })
            .catch(() => {
                return Promise.reject("Permission has not been requested");
            });
    }

    public isEnabled(): Promise<boolean> {
        return this.pushNotificationService
            .hasPermission()
            .then(() => {
                return true;
            })
            .catch(() => {
                return this.storage.get("notificationsDisabled");
            })
            .then((notificationsDisabled) => {
                if (notificationsDisabled) {
                    return Promise.reject("Notifications disabled");
                } else {
                    return Promise.resolve(true);
                }
            })
            .catch(() => {
                return Promise.reject("No permission");
            });
    }

    public enable(): Promise<boolean> {
        console.log("MessageService: Enable");
        return this.setup()
            .then(() => {
                console.log("MessageService: Get permission");
                return this.pushNotificationService.getPermission();
            })
            .then(() => {
                console.log("MessageService: Get device");
                return this.pushNotificationService.getDevice();
            })
            .then((device) => {
                console.log("MessageService: Update device");
                return this.updateDevice(device);
            });
    }

    public disable(): Promise<boolean> {
        return this.storage.set("notificationsDisabled", true).then(() => {
            return this.deleteDevice();
        });
    }

    private checkDevice(device: Device) {
        if (device) {
            this.getDevice()
                .then((storedDevice) => {
                    if (storedDevice.token !== device.token) {
                        return Promise.reject("Device needs to be updated");
                    }
                })
                .catch(() => {
                    this.updateDevice(device);
                });
        }
    }

    private updateDevice(device: Device): Promise<boolean> {
        return this.heartstepsServer
            .post("messages/device", {
                token: device.token,
                type: device.type,
            })
            .then(() => {
                return this.saveDevice(device);
            })
            .then(() => {
                return Promise.resolve(true);
            })
            .catch(() => {
                return Promise.reject(false);
            });
    }

    private getDevice(): Promise<Device> {
        return this.storage.get(storageKey).then((data: any) => {
            return Promise.resolve(new Device(data.token, data.string));
        });
    }

    private saveDevice(device: Device): Promise<boolean> {
        return this.storage.set(storageKey, {
            token: device.token,
            type: device.type,
        });
    }

    private deleteDevice(): Promise<boolean> {
        return this.storage.remove(storageKey);
    }

    public getMessage(messageId: string): Promise<Message> {
        console.log("MessageService: Get message id=" + messageId);
        return this.waitUntilSetup().then(() => {
            this.loadMessage(messageId);
        }).then(() => {
            return this.messageStorage
                .get(messageId)
                .then((data) => {
                    console.log("MessageService: returning message");
                    console.log("MessageService: data=", data);
                    return this.deserializeMessage(data);
                })
                .catch(() => {
                    return this.loadMessage(messageId);
                })
                .catch(() => {
                    console.log("MessageService: message not found");
                    return Promise.reject("Message not found");
                });
        });
    }

    public loadMessage(messageId: string): Promise<Message> {
        console.log("MessageService: loading message");
        return this.heartstepsServer
            .get("messages/" + messageId)
            .then((data) => {
                console.log("MessageService: got data=", data);
                if (data && data.context && data.context["type"]) {
                    data.type = data.context["type"];
                }
                const message = this.deserializeMessage(data);
                return this.saveMessage(message);
            });
    }

    public openMessage(messageId: string): Promise<Message> {
        return this.loadMessage(messageId).then((message) => {
            this.opened.next(message);
            return message;
        });
    }

    public serializeMessage(message: Message): any {
        return {
            id: message.id,
            type: message.type,
            title: message.title,
            body: message.body,
            context: Object.assign({}, message.context),
        };
    }

    public deserializeMessage(data: any): Message {
        console.log("MessageService.deserializeMessage(): ", data);
        const message = new Message(this.messageReceiptService);
        message.id = data.id;
        message.type = data.type;
        message.title = data.title;
        message.body = data.body;
        if (data.context) {
            message.context = data.context;
        }
        console.log("MessageService.deserializeMessage(): ", message);
        return message;
    }

    public saveMessage(message: Message): Promise<Message> {
        return this.messageStorage
            .set(message.id, this.serializeMessage(message))
            .then(() => {
                return message;
            });
    }
}
