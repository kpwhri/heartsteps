import { Component } from "@angular/core";
import { WeeklySurveyService } from "./weekly-survey.service";


@Component({
    templateUrl: './survey.component.html'
})
export class SurveyComponent {

    constructor(
        private weeklySurveyService:WeeklySurveyService
    ) {}

    next() {
        this.weeklySurveyService.nextPage();
    }

}
