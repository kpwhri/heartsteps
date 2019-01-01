import * as moment from 'moment';

import { Component, OnInit, Input } from '@angular/core';
import { DailySummary } from '@heartsteps/activity/daily-summary.model';
import { DailySummaryService } from './daily-summary.service';

@Component({
    selector: 'heartsteps-activity-daily-summary',
    templateUrl: './daily-summary.html',
    inputs: ['date']
})
export class DailySummaryComponent implements OnInit {

    @Input() date:Date;
    public formattedDate: string;
    public activitySummary: DailySummary;

    constructor(
        private dailySummaryService: DailySummaryService
    ) {}

    ngOnInit() {
        if(!this.date) {
            this.date = new Date();
        }

        const isToday:boolean = moment(new Date()).isSame(this.date);
        if(isToday) {
            this.formattedDate = 'Today ' + moment(this.date).format('MMM D')
        } else {
            this.formattedDate = moment(this.date).format('ddd MMM D')
        }
        
        this.dailySummaryService.getDate(this.date)
        .then((summary:DailySummary) => {
            this.activitySummary = summary;
        })
        .catch(() => {
            this.activitySummary = null;
        });
    }
}
