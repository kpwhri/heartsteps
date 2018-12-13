import * as moment from 'moment';

import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { DailySummary } from '@heartsteps/activity/daily-summary.model';
import { DailySummaryService } from './daily-summary.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'heartsteps-activity-daily-summary',
    templateUrl: './daily-summary.html',
    inputs: ['date']
})
export class DailySummaryComponent implements OnInit, OnDestroy {

    @Input() date:Date;
    public formattedDate: string;
    public updatedDate: string;
    public activitySummary: DailySummary;
    private updateSubscription: Subscription;

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
