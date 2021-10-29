import * as moment from 'moment';

import { Component, Input, OnDestroy } from '@angular/core';
import { DailySummary } from './daily-summary.model';
import { DailySummaryService } from './daily-summary.service';
import { Subscription } from 'rxjs';
import { c } from '@angular/core/src/render3';

@Component({
    selector: 'heartsteps-daily-summary',
    templateUrl: './daily-summary.html'
})
export class DailySummaryComponent implements OnDestroy {

    public formattedDate: string;
    public totalMinutes: number = 0;
    public vigorousMinutes: number = 0;
    public moderateMinutes: number = 0;
    public steps: number = 0;
    public miles: number = 0;

    private summary: DailySummary;

    private updateSubscription: Subscription;

    constructor(
        private dailySummaryService: DailySummaryService
    ) {
        console.log("DailySummaryComponent.constructor() point 1");
        this.updateSubscription = this.dailySummaryService.updated
            .subscribe((summary) => {
                console.log("DailySummaryComponent.constructor() point 2: summary=", summary);
                if (this.summary) {
                    console.log("DailySummaryComponent.constructor() point 2.1 - this.summary is not null");
                    console.log("this.summary.date=", this.summary.date, ", summary.date=", summary.date);
                    console.log(summary.minutes, summary.vigorousMinutes, summary.moderateMinutes, summary.steps, summary.miles);
                    if (this.summary && this.summary.date === summary.date) {
                        console.log("DailySummaryComponent.constructor() point 3");
                        this.summary = summary;
                        console.log("DailySummaryComponent.constructor() point 4");
                        this.update();
                        console.log("DailySummaryComponent.constructor() point 5");
                    } else {
                        console.log("DailySummaryComponent.constructor() point 6");
                    }
                } else {
                    console.log("DailySummaryComponent.constructor() point 2.2 - this.summary is null");
                }
            });
    }

    ngOnDestroy() {
        this.updateSubscription.unsubscribe();
    }

    @Input('summary')
    set setActivitySummary(summary) {
        if (summary) {
            this.summary = summary;
            this.update();
        }
    }

    private update() {
        console.log("DailySummaryComponent.update() point 1");
        this.totalMinutes = this.summary.minutes;
        this.vigorousMinutes = this.summary.vigorousMinutes;
        this.moderateMinutes = this.summary.moderateMinutes;
        this.steps = this.summary.steps;
        this.miles = this.summary.miles;
        console.log("DailySummaryComponent.update() point 2");
        this.formatDate();
    }

    private formatDate() {
        const summaryMoment = moment(this.summary.date);
        if (summaryMoment.isSame(new Date(), 'day')) {
            this.formattedDate = 'Today ' + summaryMoment.format('MMM D')
        } else {
            this.formattedDate = summaryMoment.format('ddd MMM D')
        }
    }

}
