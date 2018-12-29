import { Component, OnInit } from "@angular/core";
import { WeeklySurveyService } from "./weekly-survey.service";
import { Week } from "@heartsteps/weekly-survey/week.model";

@Component({
    templateUrl: './goal.component.html'
})
export class GoalComponent implements OnInit {

    public nextWeek:Week;

    constructor(
        private weeklySurveyService:WeeklySurveyService
    ) {}

    ngOnInit() {
        this.nextWeek = this.weeklySurveyService.nextWeek;
    }

    nextPage() {
        this.weeklySurveyService.nextPage();
    }

}
