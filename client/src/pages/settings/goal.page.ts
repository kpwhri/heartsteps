import { Component } from "@angular/core";
import { WeekService } from "@heartsteps/weekly-survey/week.service";
import { Location } from "@angular/common";
import { Week } from "@heartsteps/weekly-survey/week.model";


@Component({
    templateUrl: './goal.page.html'
})
export class GoalPage {

    public week: Week;

    constructor(
        private weekService: WeekService,
        private location:Location
    ) {
        this.weekService.getCurrentWeek()
        .then((week:Week) => {
            this.week = week;
        });
    }

    public goBack() {
        this.location.back();
    }

}