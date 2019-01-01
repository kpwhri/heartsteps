import { Component } from "@angular/core";
import { WeekService } from "@heartsteps/weekly-survey/week.service";
import { Location } from "@angular/common";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { CurrentWeekService } from "@heartsteps/weekly-survey/current-week.service";


@Component({
    templateUrl: './goal.page.html'
})
export class GoalPage {

    public week: Week;

    constructor(
        private currentWeekService:CurrentWeekService,
        private location:Location
    ) {
        this.currentWeekService.load()
        .then((week:Week) => {
            this.week = week;
        });
    }

    public goBack() {
        this.location.back();
    }

    public saved() {
        this.currentWeekService.set(this.week)
        .then(() => {
            this.goBack();
        });
    }

}