import { Component } from "@angular/core";
import { WeeklySurveyService } from "./weekly-survey.service";
import { Week } from "@heartsteps/weekly-survey/week.model";


@Component({
    templateUrl: './survey-review.component.html'
})
export class SurveyReviewComponent {

    nextWeek:Week;

    constructor(
        private weeklySurveyService: WeeklySurveyService
    ) {
        setTimeout(() => {
            this.nextWeek = this.weeklySurveyService.nextWeek;
        }, 100);
    }

    next() {
        this.weeklySurveyService.nextPage();
    }

}
