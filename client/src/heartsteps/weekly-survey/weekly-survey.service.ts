import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { BehaviorSubject } from "rxjs";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";
import { Week } from "./week.model";
import * as moment from 'moment';
import { WeekSerializer } from "./week.serializer";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Message } from "@heartsteps/notifications/message.model";
import { MessageService } from "@heartsteps/notifications/message.service";
import { WeekService } from "./week.service";

export class WeeklySurvey {
    public currentWeek:Week;
    public nextWeek:Week;
    public messageId:string;
    public expires:Date;
}

const storageKey:string = 'weekly-survey';

@Injectable()
export class WeeklySurveyService {

    public survey:BehaviorSubject<WeeklySurvey> = new BehaviorSubject(undefined);

    constructor(
        private storage:StorageService,
        private weekService: WeekService,
        private weekSerializer: WeekSerializer,
        private heartstepsServer: HeartstepsServer,
        private messageReceiptService: MessageReceiptService,
        private messageService: MessageService
    ) {}

    public setup():Promise<boolean> {
        return this.get()
        .then((survey:WeeklySurvey) => {
            this.survey.next(survey);
            return true;
        })
        .catch(() => {
            return Promise.resolve(true);
        });
    }

    public testReflectionNotification():Promise<boolean> {
        return this.heartstepsServer.post('weeks/current/send', {})
        .then(() => {
            return true;
        });
    }

    public testReflection():Promise<boolean> {
        return Promise.all([
            this.weekService.getCurrentWeek(),
            this.weekService.getNextWeek()
        ])
        .then((results) => {
            const currentWeek = results[0];
            const nextWeek = results[1];
            const expires = moment().add(1, 'hours').toDate();
            return this.set(currentWeek, nextWeek, expires);
        })
        .then(() => {
            return true;
        })
    }

    public processNotification(message:Message):Promise<boolean> {
        const currentWeek = this.weekSerializer.deserialize(message.context.currentWeek);
        const nextWeek = this.weekSerializer.deserialize(message.context.nextWeek);
        const expires = moment().add(1, 'days').toDate();
        return this.set(currentWeek, nextWeek, expires, message.id)
        .then(() => {
            return this.messageService.createNotification(message.id, 'Weekly reflection time')
        });
    }

    public complete():Promise<boolean> {
        return this.get()
        .then((survey:WeeklySurvey) => {
            if(survey.messageId) {
                return this.messageReceiptService.engaged(survey.messageId);
            } else {
                return true;
            }
        })
        .catch(() => {
            return Promise.resolve(true);
        })
        .then(() => {
            return this.clear();
        });
    }

    public clear():Promise<boolean> {
        return this.storage.remove(storageKey)
        .then(() => {
            this.survey.next(null);
            return true;
        });
    }

    public checkExpiration():Promise<boolean> {
        return this.get()
        .then((survey) => {
            if (survey.expires <= new Date()) {
                return this.clear()
                .then(() => {
                    return Promise.resolve(true);
                });
            } else {
                return Promise.resolve(false);
            }
        })
        .catch(() => {
            return Promise.resolve(true);
        });
    }

    public set(currentWeek:Week, nextWeek:Week, expireDate?:Date, messageId?:string):Promise<WeeklySurvey> {
        const survey = new WeeklySurvey();
        survey.currentWeek = currentWeek;
        survey.nextWeek = nextWeek;
        if (expireDate) {
            survey.expires = expireDate;
        }
        if (messageId) {
            survey.messageId = messageId;
        }
        return this.storage.set(storageKey, this.serialize(survey))
        .then((survey:WeeklySurvey) => {
            this.survey.next(survey);
            return survey;
        });
    }

    public get():Promise<WeeklySurvey> {
        return this.storage.get(storageKey)
        .then((data) => {
            return this.deserialize(data);
        });
    }

    private serialize(survey:WeeklySurvey):any {
        return {
            currentWeek: this.weekSerializer.serialize(survey.currentWeek),
            nextWeek: this.weekSerializer.serialize(survey.nextWeek),
            messageId: survey.messageId,
            expires: survey.expires
        }
    }

    private deserialize(data:any):WeeklySurvey {
        const survey = new WeeklySurvey();
        survey.currentWeek = this.weekSerializer.deserialize(data['currentWeek']);
        survey.nextWeek = this.weekSerializer.deserialize(data['nextWeek']);
        if(data['expires']) survey.expires = data['expires'];
        if(data['messageId']) survey.messageId = data['messageId'];
        return survey;
    }
 
}