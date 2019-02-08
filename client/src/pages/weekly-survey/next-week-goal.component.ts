import { Component, OnInit, Output, EventEmitter } from "@angular/core";
import { Week } from "@heartsteps/weekly-survey/week.model";
import { ActivatedRoute } from "@angular/router";

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
        this.nextWeek = this.activatedRoute.snapshot.data['weeks'][1];
    }

    nextPage() {
        this.next.emit();
    }

}
