import { Component, OnInit, Output, EventEmitter } from "@angular/core";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { ActivatedRoute } from "@angular/router";
import { WeeklySurvey } from "@heartsteps/weekly-survey/weekly-survey.service";

@Component({
    templateUrl: './next-week-goal.component.html'
})
export class NextWeekGoalComponent implements OnInit {

    public nextWeek:Week;
    @Output('next') next:EventEmitter<boolean> = new EventEmitter();

    constructor(
        private activatedRoute: ActivatedRoute
    ) {}

    ngOnInit() {
        const weeklySurvey:WeeklySurvey = this.activatedRoute.snapshot.data['weeklySurvey'];
        this.nextWeek = weeklySurvey.nextWeek;
    }

    nextPage() {
        this.next.emit();
    }

}
