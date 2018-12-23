import { Component } from "@angular/core";
import { WeeklySurveyService } from "./weekly-survey.service";


@Component({
    templateUrl: './goal.component.html'
})
export class GoalComponent {

    constructor(
        private weeklySurveyService:WeeklySurveyService
    ) {}

    next() {
        this.weeklySurveyService.nextPage();
    }

}
