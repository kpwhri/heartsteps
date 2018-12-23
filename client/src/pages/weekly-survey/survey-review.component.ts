import { Component } from "@angular/core";
import { WeeklySurveyService } from "./weekly-survey.service";


@Component({
    templateUrl: './survey-review.component.html'
})
export class SurveyReviewComponent {

    constructor(
        private weeklySurveyService: WeeklySurveyService
    ) {}

    next() {
        this.weeklySurveyService.nextPage();
    }

}
