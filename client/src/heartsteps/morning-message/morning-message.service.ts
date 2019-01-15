import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { MorningMessage } from "./morning-message.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";

const storageKey:string = 'morning-message';

@Injectable()
export class MorningMessageService {

    constructor(
        private storage: StorageService,
        private heartstepsServer: HeartstepsServer
    ){}

    public get():Promise<MorningMessage> {
        return this.storage.get(storageKey)
        .then((data) => {
            return this.deserialize(data);
        })
        .catch(() => {
            return this.load();
        });
    }

    public set(message: MorningMessage):Promise<MorningMessage> {
        return this.storage.set(storageKey, this.serialize(message))
        .then(() => {
            return message;
        });
    }

    public load():Promise<MorningMessage> {
        const today:string = moment().format("YYYY-MM-DD");
        return this.heartstepsServer.get('morning-messages/' + today)
        .then((data) => {
            const message = this.deserialize(data);
            return message;
        });
    }

    public deserialize(data:any):MorningMessage {
        const message = new MorningMessage();
        message.id = data.id;
        message.text = data.text;
        message.anchor = data.anchor;
        return message;
    }

    public serialize(message:MorningMessage):any {
        return {
            id: message.id,
            text: message.text,
            anchor: message.anchor
        }
    }

}
