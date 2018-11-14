import * as moment from 'moment';

import { Component, OnInit } from '@angular/core';
import { ActivityLogService } from '@heartsteps/activity/activity-log.service';
import { DailySummary } from '@heartsteps/activity/daily-summary.model';
import { DailySummaryFactory } from './daily-summary.factory';

@Component({
    selector: 'heartsteps-activity-daily-summary',
    templateUrl: './daily-summary.html',
    providers: [DailySummaryFactory],
})
export class DailySummaryComponent implements OnInit {

    public date: Date;
    public formattedDate: string;
    public activitySummary: DailySummary;

    constructor(
        private dailySummary: DailySummaryFactory
    ) {
        this.date = new Date();
        const isToday:boolean = moment(new Date()).isSame(this.date);
        if(isToday) {
            this.formattedDate = 'Today ' + moment(this.date).format('MMM D')
        } else {
            this.formattedDate = moment(this.date).format('ddd MMM D')
        }
    }

    ngOnInit() {
        this.dailySummary.date(this.date).subscribe((dailySummary: DailySummary) => {
            this.activitySummary = dailySummary;
        });
    }
}
