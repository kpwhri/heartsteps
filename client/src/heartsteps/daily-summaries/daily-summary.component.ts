import * as moment from 'moment';

import { Component, Input } from '@angular/core';
import { DailySummary } from './daily-summary.model';

@Component({
    selector: 'heartsteps-daily-summary',
    templateUrl: './daily-summary.html'
})
export class DailySummaryComponent {

    public formattedDate: string;
    public activitySummary: DailySummary;

    constructor() {}

    @Input('summary')
    set setActivitySummary(summary) {
        if(summary) {
            this.activitySummary = summary;
            const summaryMoment = moment(this.activitySummary.date);
            if(summaryMoment.isSame(new Date(), 'day')) {
                this.formattedDate = 'Today ' + summaryMoment.format('MMM D')
            } else {
                this.formattedDate = summaryMoment.format('ddd MMM D')
            }
        }
    }
}
