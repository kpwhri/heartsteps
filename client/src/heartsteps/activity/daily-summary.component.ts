import * as moment from 'moment';

import { Component, OnInit } from '@angular/core';
import { ActivityLogService } from '@heartsteps/activity/activity-log.service';
import { DailySummary } from '@heartsteps/activity/daily-summary.model';

@Component({
    selector: 'heartsteps-activity-daily-summary',
    templateUrl: './daily-summary.html',
    providers: [ActivityLogService],
})
export class DailySummaryComponent implements OnInit {

    public date: Date;
    public formattedDate: string;
    public activitySummary: DailySummary;

    constructor(
        private activityLogService: ActivityLogService
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
        this.activityLogService.getSummary(this.date)
        .then((dailySummary: DailySummary) => {
            this.activitySummary = dailySummary;
        })
        .catch(() => {
            this.activitySummary = null;
        })
    }
}
