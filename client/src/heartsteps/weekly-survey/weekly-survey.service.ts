import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { Router } from "@angular/router";
import { BehaviorSubject } from "rxjs";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";
import { LocalNotifications } from '@ionic-native/local-notifications';

export class WeeklySurvey {
    public weekId:string
    public messageId:string
    public expires:Date
}

const storageKey:string = 'weekly-survey';

@Injectable()
export class WeeklySurveyService {

    public survey:BehaviorSubject<WeeklySurvey>

    constructor(
        private storage:StorageService,
        private messageReceiptService: MessageReceiptService,
        private router:Router,
        private localNotifications: LocalNotifications
    ){
        this.survey = new BehaviorSubject(null);
        this.getSurvey()
        .then((survey:WeeklySurvey) => {
            this.survey.next(survey);
        });
    }

    public complete() {
        this.getSurvey()
        .then((survey:WeeklySurvey) => {
            if(survey.messageId) {
                this.messageReceiptService.engaged(survey.messageId);
            }
            this.clear();
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
        return this.getSurvey()
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

    public set(weekId:string, messageId?:string):Promise<WeeklySurvey> {
        const expireDate:Date = new Date();
        expireDate.setDate(expireDate.getDate() + 1);
        
        return this.setSurvey(weekId, messageId, expireDate)
        .then((survey:WeeklySurvey) => {
            this.localNotifications.schedule({
                id: Number(weekId),
                text: 'Hello Im the weekly survey notification!'
            })
            this.survey.next(survey);
            return survey;
        });
    }

    public show():Promise<boolean> {
        return this.getSurvey()
        .then((survey:WeeklySurvey) => {
            this.router.navigate(['weekly-survey', survey.weekId]);
            return true;
        });
    }

    private getSurvey():Promise<WeeklySurvey> {
        return this.storage.get(storageKey)
        .then((data) => {
            const survey = new WeeklySurvey();
            survey.weekId = data.weekId;
            survey.messageId = data.messageId;
            survey.expires = data.expires;
            return survey;
        });
    }

    private setSurvey(weekId:string, messageId:string, expires:Date):Promise<WeeklySurvey> {
        return this.storage.set(storageKey, {
            weekId: weekId,
            messageId: messageId,
            expires: expires
        })
        .then(() => {
            return this.getSurvey();
        });
    }

}