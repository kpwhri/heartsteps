import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { MorningMessage } from "./morning-message.model";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { MessageReceiptService } from '@heartsteps/notifications/message-receipt.service';
import { Message } from '@heartsteps/notifications/message.model';

const storageKey:string = 'morning-message';

@Injectable()
export class MorningMessageService {

    constructor(
        private storage: StorageService,
        private heartstepsServer: HeartstepsServer,
        private messageReceiptService: MessageReceiptService
    ) {}

    public get():Promise<MorningMessage> {
        return this.getMessage()
        .catch(() => {
            return this.load();
        });
    }

    public submitSurvey(values: any): Promise<boolean> {
        return this.get()
        .then((morningMessage) => {
            const formattedDate:string = moment(morningMessage.date).format("YYYY-MM-DD");
            return this.heartstepsServer.post(
                'morning-messages/' + formattedDate + '/survey',
                values
            )
            .then((response) => {
                morningMessage.response = response;
                return this.set(morningMessage);
            })
        })
        .then(() => {
            return true;
        });
    }

    public processMessage(message: Message):Promise<MorningMessage> {
        return this.set({
            id: message.id,
            date: message.context.date,
            notification: message.body,
            text: message.context.text,
            anchor: message.context.anchor,
            survey: message.context.survey,
            response: undefined,
            surveyComplete: false
        });
    }

    private getMessage():Promise<MorningMessage> {
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
                });
            }
        });
    }

    public set(message: MorningMessage):Promise<MorningMessage> {
        return this.storage.set(storageKey, this.serialize(message))
        .then(() => {
            return message;
        });
    }

    public complete():Promise<boolean> {
        return this.get()
        .then((morningMessage) => {
            morningMessage.surveyComplete = true;
            return this.set(morningMessage);
        })
        .then((morningMessage) => {
            if(morningMessage.id) {
                return this.messageReceiptService.engaged(morningMessage.id)
            } else {
                return Promise.resolve(true)
            }
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
        })
        .then((morningMessage) => {
            return this.heartstepsServer.get('morning-messages/' + today + '/survey/response')
            .then((response) => {
                morningMessage.response = response;
                return this.set(morningMessage);
            });
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
        message.survey = data.survey;
        message.response = data.response;
        message.surveyComplete = data.surveyComplete;
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
            anchor: message.anchor,
            survey: message.survey,
            response: message.response,
            surveyComplete: message.surveyComplete
        }
    }

}
