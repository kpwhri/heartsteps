import { Component } from "@angular/core";
import { WeeklySurveyService } from "./weekly-survey.service";


@Component({
    selector: 'page-weekly-survey-start',
    templateUrl: './survey-start.html'
})
export class SurveyStartPage {

    constructor(
        private weeklySurveyService:WeeklySurveyService
    ) {}

    next() {
        this.weeklySurveyService.nextPage();
    }
}