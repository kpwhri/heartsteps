import { Component, OnInit, OnDestroy } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { Week } from '@heartsteps/weekly-survey/week.model';
import { CurrentWeekService } from '@heartsteps/weekly-survey/current-week.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'page-plan',
    templateUrl: 'plan.page.html',
    providers: [DateFactory]
})
export class PlanPage implements OnInit, OnDestroy {

    private week:Week;
    private weekSubscription: Subscription;

    constructor(
        private currentWeekService: CurrentWeekService
    ) {}

    ngOnInit() {
        this.weekSubscription = this.currentWeekService.week.subscribe((week) => {
            this.week = week;
        });
    }

    ngOnDestroy() {
        if(this.weekSubscription) {
            this.weekSubscription.unsubscribe();
        }
    }
}
