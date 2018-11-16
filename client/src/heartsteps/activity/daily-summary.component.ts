import * as moment from 'moment';

import { Component, OnInit, OnDestroy } from '@angular/core';
import { DailySummary } from '@heartsteps/activity/daily-summary.model';
import { DailySummaryService } from './daily-summary.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'heartsteps-activity-daily-summary',
    templateUrl: './daily-summary.html',
})
export class DailySummaryComponent implements OnInit, OnDestroy {

    public date: Date;
    public formattedDate: string;
    public updatedDate: string;
    public activitySummary: DailySummary;
    private updateSubscription: Subscription;

    constructor(
        private dailySummaryService: DailySummaryService
    ) {
        this.date = new Date();
        const isToday:boolean = moment(new Date()).isSame(this.date);
        if(isToday) {
            this.formattedDate = 'Today ' + moment(this.date).format('MMM D')
        } else {
            this.formattedDate = moment(this.date).format('ddd MMM D')
        }
    }

    public refresh() {
        this.dailySummaryService.getDate(this.date);
    }

    ngOnInit() {
        this.updateSubscription = this.dailySummaryService.summaries.subscribe((summaries:Array<DailySummary>) => {
            summaries.forEach((summary:DailySummary) => {
                if(summary.date == moment(this.date).format('YYYY-MM-DD')) {
                    this.activitySummary = summary;
                    this.updatedDate = moment(this.date).format('YYYY MM DD h:m')
                }
            });
        });
        this.dailySummaryService.getDate(this.date);
    }

    ngOnDestroy() {
        this.updateSubscription.unsubscribe();
    }
}
