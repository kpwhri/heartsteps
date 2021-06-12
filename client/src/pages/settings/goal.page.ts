import { Component } from "@angular/core";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { CurrentWeekService } from "@heartsteps/current-week/current-week.service";
import { Router } from "@angular/router";

@Component({
    templateUrl: "./goal.page.html",
})
export class GoalPage {
    public week: Week;

    constructor(
        private currentWeekService: CurrentWeekService,
        private router: Router
    ) {
        this.currentWeekService.get().then((week: Week) => {
            this.week = week;
        });
    }

    public goBack() {
        this.router.navigate([
            {
                outlets: {
                    modal: null,
                },
            },
        ]);
    }

    public saved() {
        this.currentWeekService.set(this.week).then(() => {
            this.goBack();
        });
    }
}
