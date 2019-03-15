import { Injectable } from "@angular/core";
import { Resolve, ActivatedRouteSnapshot } from "@angular/router";
import { WeeklySurveyService, WeeklySurvey } from "@heartsteps/weekly-survey/weekly-survey.service";


@Injectable()
export class WeeklySurveyResolver implements Resolve<WeeklySurvey> {

    constructor(
        private weeklySurveyService: WeeklySurveyService
    ){}

    resolve(route:ActivatedRouteSnapshot) {
        return this.weeklySurveyService.get() 
    }
}
