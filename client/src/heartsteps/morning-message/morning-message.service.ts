import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { MorningMessage } from "./morning-message.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { MessageService } from '@heartsteps/notifications/message.service';

const storageKey:string = 'morning-message';

@Injectable()
export class MorningMessageService {

    constructor(
        private storage: StorageService,
        private heartstepsServer: HeartstepsServer,
        private messageService: MessageService
    ){}

    public get():Promise<MorningMessage> {
        return this.storage.get(storageKey)
        .then((data) => {
            return this.deserialize(data);
        });
    }

    public set(message: MorningMessage):Promise<MorningMessage> {
        return this.storage.set(storageKey, this.serialize(message))
        .then(() => {
            return this.messageService.createNotification(message.id, message.notification);
        })
        .then(() => {
            return message;
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
        message.notification = data.notification;
        message.text = data.text;
        message.anchor = data.anchor;
        return message;
    }

    public serialize(message:MorningMessage):any {
        return {
            id: message.id,
            notification: message.notification,
            text: message.text,
            anchor: message.anchor
        }
    }

}
