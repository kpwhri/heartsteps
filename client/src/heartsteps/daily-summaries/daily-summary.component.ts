import * as moment from 'moment';

import { Component, Input } from '@angular/core';
import { DailySummary } from './daily-summary.model';
import { DailySummaryService } from './daily-summary.service';

@Component({
    selector: 'heartsteps-daily-summary',
    templateUrl: './daily-summary.html'
})
export class DailySummaryComponent {

    public formattedDate: string;
    public activitySummary: DailySummary;

    constructor(
        private dailySummaryService: DailySummaryService
    ) {}

    @Input('summary')
    set setActivitySummary(summary) {
        if(summary) {
            this.update(summary);
        }
    }

    @Input('date')
    set setDate(date) {
        if(date) {
            this.dailySummaryService.get(date)
            .then((summary) => {
                this.update(summary);
            })
            .catch(() => {
                console.log('Daily summary could not get date');
            });
        }
    }

    private update(summary: DailySummary) {
        this.activitySummary = summary;
        const summaryMoment = moment(this.activitySummary.date);
        if(summaryMoment.isSame(new Date(), 'day')) {
            this.formattedDate = 'Today ' + summaryMoment.format('MMM D')
        } else {
            this.formattedDate = summaryMoment.format('ddd MMM D')
        }
    }
}
