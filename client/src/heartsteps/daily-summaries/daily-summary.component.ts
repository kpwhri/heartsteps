import * as moment from 'moment';

import { Component, Input, OnDestroy } from '@angular/core';
import { DailySummary } from './daily-summary.model';
import { DailySummaryService } from './daily-summary.service';
import { Subscription } from 'rxjs';

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
        this.updateSubscription = this.dailySummaryService.updated
        .subscribe((summary) => {
            if(this.summary && this.summary.date === summary.date) {
                this.summary = summary;
                this.update();
            }
        });
    }

    ngOnDestroy() {
        this.updateSubscription.unsubscribe();
    }

    @Input('summary')
    set setActivitySummary(summary) {
        if(summary) {
            this.summary = summary;
            this.update();
        }
    }

    private update() {
        this.totalMinutes = this.summary.minutes;
        this.vigorousMinutes = this.summary.vigorousMinutes;
        this.moderateMinutes = this.summary.moderateMinutes;
        this.steps = this.summary.steps;
        this.miles = this.summary.miles;
        
        this.formatDate();
    }

    private formatDate() {
        const summaryMoment = moment(this.summary.date);
        if(summaryMoment.isSame(new Date(), 'day')) {
            this.formattedDate = 'Today ' + summaryMoment.format('MMM D')
        } else {
            this.formattedDate = summaryMoment.format('ddd MMM D')
        }
    }

}
