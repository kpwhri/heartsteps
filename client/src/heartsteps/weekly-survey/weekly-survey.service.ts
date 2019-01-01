import { Injectable } from "@angular/core";
import { StorageService } from "@infrastructure/storage.service";
import { Router } from "@angular/router";


@Injectable()
export class WeeklySurveyService {

    constructor(
        private storage:StorageService,
        private router:Router
    ){}

    public clear() {
        console.log("Clear the weekly survey....")
    }

    public set(weekId:string, messageId?:string):Promise<boolean> {
        return this.setSurvey(weekId) // set timeout in 24 hours....
        .then(() => {
            return true;
        });
        // show notification on dashboard
    }

    public show():Promise<boolean> {
        return this.getSurvey()
        .then((weekId:string) => {
            this.router.navigate(['weekly-survey', weekId]);
            return true;
        });
    }

    public isSet():Promise<boolean> {
        return this.getSurvey()
        .catch(() => {
            return Promise.reject("No weekly survey");
        });
    }

    private getSurvey() {
        return this.storage.get('weekly-survey');
    }

    private setSurvey(weekId:string) {
        return this.storage.set('weekly-survey', weekId);
    }

}