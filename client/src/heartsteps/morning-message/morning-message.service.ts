import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { MorningMessage } from "./morning-message.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { MessageService } from '@heartsteps/notifications/message.service';
import { MessageReceiptService } from '@heartsteps/notifications/message-receipt.service';

const storageKey:string = 'morning-message';

@Injectable()
export class MorningMessageService {

    constructor(
        private storage: StorageService,
        private heartstepsServer: HeartstepsServer,
        private messageService: MessageService,
        private messageReceiptService: MessageReceiptService
    ){}

    public get():Promise<MorningMessage> {
        return this.storage.get(storageKey)
        .then((data) => {
            return this.deserialize(data);
        })
        .then((morningMessage) => {
            if(moment().isSame(morningMessage.date, "day")) {
                return morningMessage;
            } else {
                this.clear()
                .then(() => {
                    return Promise.reject('Morning message expired');
                })
            }
        });
    }

    public set(message: MorningMessage):Promise<MorningMessage> {
        return this.storage.set(storageKey, this.serialize(message))
        .then(() => {
            if(message.id) {
                return this.messageService.createNotification(message.id, message.notification);
            } else {
                return Promise.resolve(true);
            }
        })
        .then(() => {
            return message;
        });
    }

    public complete():Promise<boolean> {
        return this.get()
        .then((morningMessage) => {
            if(morningMessage.id) {
                return this.messageReceiptService.engaged(morningMessage.id)
            } else {
                return Promise.resolve(true)
            }
        })
        .then(() => {
            return this.clear();
        })
        .catch(() => {
            return Promise.resolve(true);
        });
    }

    public clear():Promise<boolean> {
        return this.storage.remove(storageKey)
        .then(() => {
            return true;
        });
    }

    public load():Promise<MorningMessage> {
        const today:string = moment().format("YYYY-MM-DD");
        return this.heartstepsServer.get('morning-messages/' + today)
        .then((data) => {
            const message = this.deserialize(data);
            return this.set(message);
        });
    }

    public requestNotification():Promise<boolean> {
        const today:string = moment().format("YYYY-MM-DD");
        return this.heartstepsServer.post('morning-messages/' + today, {})
        .then(() => {
            return true;
        });
    }

    public deserialize(data:any):MorningMessage {
        const message = new MorningMessage();
        message.id = data.id;
        message.date = moment(data.date, 'YYYY-MM-DD').toDate();
        message.notification = data.notification;
        message.text = data.text;
        message.anchor = data.anchor;
        return message;
    }

    public serialize(message:MorningMessage):any {
        let messageId:string = undefined;
        if(message.id) {
            messageId = message.id;
        }
        return {
            id: messageId,
            date: moment(message.date).format('YYYY-MM-DD'),
            notification: message.notification,
            text: message.text,
            anchor: message.anchor
        }
    }

}
