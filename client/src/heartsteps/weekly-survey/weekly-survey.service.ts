import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";
import { Week } from "./week.model";
import * as moment from 'moment';
import { WeekSerializer } from "./week.serializer";
import { HeartstepsServer } from "@infrastructure/heartsteps-server.service";
import { Message } from "@heartsteps/notifications/message.model";
import { WeekService } from "./week.service";
import { ReflectionTimeService } from "./reflection-time.service";

export class WeeklySurvey {
    public currentWeek:Week;
    public nextWeek:Week;
    public messageId:string;
    public starts: Date;
    public expires:Date;
    public completed: boolean;
    public questions: any;
    public response: any;
}

const storageKey:string = 'weekly-survey';

@Injectable()
export class WeeklySurveyService {

    constructor(
        private storage:StorageService,
        private weekService: WeekService,
        private weekSerializer: WeekSerializer,
        private heartstepsServer: HeartstepsServer,
        private reflectionTimeService: ReflectionTimeService,
        private messageReceiptService: MessageReceiptService
    ) {}

    public setup():Promise<boolean> {
        return this.get()
        .then(() => {
            return true;
        });
    }

    public testReflectionNotification():Promise<boolean> {
        return this.heartstepsServer.post('weeks/current/send', {})
        .then(() => {
            return true;
        });
    }

    public testReflection():Promise<boolean> {
        return this.load()
        .then((weeklySurvey) => {
            weeklySurvey.starts = new Date();
            weeklySurvey.expires = moment().add(5, 'minutes').toDate();
            return this.save(weeklySurvey);
        })
        .then(() => {
            return true;
        });
    }

    public processMessage(message:Message):Promise<WeeklySurvey> {
        const currentWeek = this.weekSerializer.deserialize(message.context.currentWeek);
        const nextWeek = this.weekSerializer.deserialize(message.context.nextWeek);
        return this.set(currentWeek, nextWeek, message.id);
    }

    public submitSurvey(values:any) {
        return this.get()
        .then((weeklySurvey) => {
            return this.weekService.submitWeekSurvey(weeklySurvey.currentWeek, values)
            .then(() => {
                weeklySurvey.response = values;
                return this.save(weeklySurvey);
            });
        });
    }

    public complete():Promise<boolean> {
        return this.get()
        .then((weeklySurvey) => {
            weeklySurvey.completed = true;
            return this.save(weeklySurvey);
        })
        .then((survey:WeeklySurvey) => {
            if(survey.messageId) {
                return this.messageReceiptService.engaged(survey.messageId);
            } else {
                return true;
            }
        })
        .catch(() => {
            return Promise.resolve(true);
        });
    }

    private load():Promise<WeeklySurvey> {
        return Promise.all([
            this.weekService.getCurrentWeek(),
            this.weekService.getNextWeek()
        ])
        .then((results) => {
            const currentWeek = results[0];
            const nextWeek = results[1];
            return this.set(currentWeek, nextWeek);
        });
    }

    private save(weeklySurvey):Promise<WeeklySurvey> {
        return this.storage.set(storageKey, this.serialize(weeklySurvey))
        .then(() => {
            return weeklySurvey;
        });
    }

    public clear():Promise<boolean> {
        return this.storage.remove(storageKey)
        .then(() => {
            return true;
        });
    }

    public get():Promise<WeeklySurvey> {
        return this.storage.get(storageKey)
        .then((data) => {
            return this.deserialize(data);
        })
        .catch(() => {
            return this.load();
        });
    }

    public getAvailableSurvey(): Promise<WeeklySurvey> {
        return this.get()
        .then((weeklySurvey) => {
            if(moment().isAfter(weeklySurvey.expires)) {
                return this.clear()
                .then(() => {
                    return Promise.reject("After weekly reflection time");
                })
            }
            if(moment().isBefore(weeklySurvey.starts)) {
                return Promise.reject("Before reflection time");
            }
            if(weeklySurvey.completed) {
                return Promise.reject("Weekly survey completed");
            }
            return Promise.resolve(weeklySurvey);
        });
    }

    public set(currentWeek:Week, nextWeek:Week, messageId?:string):Promise<WeeklySurvey> {
        const survey = new WeeklySurvey();
        survey.currentWeek = currentWeek;
        survey.nextWeek = nextWeek;
        if (messageId) {
            survey.messageId = messageId;
        }
        return this.reflectionTimeService.getTime()
        .then((reflectionTime) => {
            const daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
            const reflectionDate:Date = currentWeek.getDays().find((day) => {
                const dayName = daysOfWeek[day.getDay()];
                if(dayName === reflectionTime.day) {
                    return true;
                } else {
                    return false;
                }
            });
            reflectionDate.setHours(reflectionTime.time.getHours());
            reflectionDate.setMinutes(reflectionTime.time.getMinutes());

            survey.starts = reflectionDate;
            survey.expires = moment(reflectionDate).add(1, 'days').toDate();
            return this.save(survey);
        })
        .then((weeklySurvey) => {
            return this.weekService.getWeekSurvey(survey.currentWeek)
            .then((survey) => {
                weeklySurvey.completed = survey.completed;
                weeklySurvey.questions = survey.questions;
                return this.save(weeklySurvey);
            });
        });
    }

    private serialize(survey:WeeklySurvey):any {
        return {
            currentWeek: this.weekSerializer.serialize(survey.currentWeek),
            nextWeek: this.weekSerializer.serialize(survey.nextWeek),
            messageId: survey.messageId,
            starts: survey.starts,
            expires: survey.expires,
            completed: survey.completed,
            questions: survey.questions,
            response: survey.response
        }
    }

    private deserialize(data:any):WeeklySurvey {
        const survey = new WeeklySurvey();
        survey.currentWeek = this.weekSerializer.deserialize(data['currentWeek']);
        survey.nextWeek = this.weekSerializer.deserialize(data['nextWeek']);
        if(data['expires']) survey.expires = data['expires'];
        if(data['starts']) survey.starts = data['starts'];
        if(data['messageId']) survey.messageId = data['messageId'];
        if(data['completed']) survey.completed = data['completed'];
        survey.questions = data['questions'];
        survey.response = data['response'];
        return survey;
    }
 
}