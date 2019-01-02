import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { Router } from "@angular/router";
import { BehaviorSubject } from "rxjs";
import { MessageReceiptService } from "@heartsteps/notifications/message-receipt.service";

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
        private router:Router
    ){
        this.survey = new BehaviorSubject(null);
        this.getSurvey()
        .then((survey:WeeklySurvey) => {
            this.survey.next(survey);
        })
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

    public clear() {
        this.storage.remove(storageKey);
        this.survey.next(null);
    }

    public set(weekId:string, messageId?:string):Promise<WeeklySurvey> {
        return this.setSurvey(weekId) // set timeout in 24 hours....
        .then((survey:WeeklySurvey) => {

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
            this.weekId = data.weekId;
            this.messageId = data.messageId;
            this.expires = data.expires;

            const survey = new WeeklySurvey();
            survey.weekId = data.weekId;
            survey.messageId = data.messageId;
            survey.expires = data.expires;
            return survey;
        });
    }

    private setSurvey(weekId:string):Promise<WeeklySurvey> {
        return this.storage.set(storageKey, {
            weekId: weekId
        })
        .then(() => {
            return this.getSurvey();
        });
    }

}