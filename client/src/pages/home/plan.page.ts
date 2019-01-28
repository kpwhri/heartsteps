import { Component, OnInit, OnDestroy } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { Week } from '@heartsteps/weekly-survey/week.model';
import { CurrentWeekService } from '@heartsteps/current-week/current-week.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'page-plan',
    templateUrl: 'plan.page.html',
    providers: [DateFactory]
})
export class PlanPage implements OnInit {

    public week:Week;

    constructor(
        private currentWeekService: CurrentWeekService
    ) {}

    ngOnInit() {
        this.currentWeekService.get()
        .then((week) => {
            this.week = week;
        });
    }
}
