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
        return this.setMessageState(messageId, 'received');
    }

    opened(messageId:string): Promise<boolean> {
        return this.setMessageState(messageId, 'opened');
    }

    engaged(messageId:string) {
        return this.setMessageState(messageId, 'engaged');
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
                return Promise.reject("Message state already set.")
            }

            messages[messageId][state] = new Date().toISOString();
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
        return Promise.resolve(true);
    }
}
