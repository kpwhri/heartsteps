import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { Storage } from "@ionic/storage";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";

const storageKey: string = "message-receipts";

@Injectable()
export class MessageReceiptService {

    constructor(
        private storage: Storage,
        private heartstepsServer: HeartstepsServer
    ){}

    received(messageId:string): Promise<boolean> {
        return this.sendMessageState(messageId, 'received');
    }

    opened(messageId:string): Promise<boolean> {
        return this.sendMessageState(messageId, 'opened');
    }

    engaged(messageId:string) {
        return this.sendMessageState(messageId, 'engaged');
    }

    private sendMessageState(messageId: string, state: string):Promise<boolean> {
        const messageObj: any = {
            id: messageId
        };
        messageObj[state] = moment().utc().format('YYYY-MM-DD HH:mm:ss')
        return this.heartstepsServer.post('messages', messageObj)
        .then(() => {
            return true;
        });
    }

    private setMessageState(messageId: string, state: string): Promise<boolean> {
        return this.storage.get(storageKey)
        .then((messages) => {
            if(!messages) {
                messages = {}
            }
            if (!messages[messageId]) {
                messages[messageId] = {}
            }
            if (messages[messageId][state]) {
                return Promise.reject("Message state already set")
            }

            messages[messageId][state] = moment().utc().format('YYYY-MM-DD HH:mm:ss')
            return this.storage.set(storageKey, messages)
        })
        .then(() => {
            return Promise.resolve(true);
        })
        .catch((error) => {
            return Promise.reject(error);
        });
    }

    sync(): Promise<boolean> {
        return this.storage.get(storageKey)
        .then((messages) => {
            if(!messages || Object.keys(messages).length < 1) {
                return Promise.resolve(true)
            }
            const messageList:Array<any> = [];
            Object.keys(messages).forEach((key) => {
                const message = messages[key];
                message.id = key;
                messageList.push(message);
            })
            return this.heartstepsServer.post('/messages', messageList);
        })
        .then(() => {
            return this.storage.set(storageKey, {})
        })
        .then(() => {
            return Promise.resolve(true);
        });
    }
}
