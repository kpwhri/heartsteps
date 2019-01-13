import { Component } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { Week } from '@heartsteps/weekly-survey/week.model';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'page-plan',
    templateUrl: 'plan.page.html',
    providers: [DateFactory]
})
export class PlanPage {

    private week:Week

    constructor(
        activatedRoute:ActivatedRoute
    ) {
        this.week = activatedRoute.snapshot.data['week'];
    }
}
