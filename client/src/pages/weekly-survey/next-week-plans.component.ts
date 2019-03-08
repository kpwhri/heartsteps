import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { WeeklySurvey } from "@heartsteps/weekly-survey/weekly-survey.service";

@Component({
    templateUrl: './next-week-plans.component.html'
})
export class NextWeekPlansComponent implements OnInit {

    @Output('next') next:EventEmitter<boolean> = new EventEmitter();
    public nextWeek: Week;

    constructor(
        private activatedRoute: ActivatedRoute
    ) {}

    ngOnInit() {
        const weeklySurvey: WeeklySurvey = this.activatedRoute.snapshot.data['weeklySurvey'];
        this.nextWeek = weeklySurvey.nextWeek; 
    }

    nextPage() {
        this.next.emit();
    }

}
