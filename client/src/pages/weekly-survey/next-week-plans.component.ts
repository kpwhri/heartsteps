import { Component, Output, EventEmitter, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { Week } from "@heartsteps/weekly-survey/week.model";

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
        this.nextWeek = this.activatedRoute.snapshot.data['weeks'][1];
    }

    nextPage() {
        this.next.emit();
    }

}
