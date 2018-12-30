import { Component } from "@angular/core";
import { WeeklySurveyService } from "./weekly-survey.service";


@Component({
    templateUrl: './survey-review.component.html'
})
export class SurveyReviewComponent {

    goal: number;

    constructor(
        private weeklySurveyService: WeeklySurveyService
    ) {
        this.goal = this.weeklySurveyService.nextWeek.goal;
    }

    next() {
        this.weeklySurveyService.nextPage();
    }

}
