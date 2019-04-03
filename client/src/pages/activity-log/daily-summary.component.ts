import { Component, Input, OnDestroy } from "@angular/core";
import { DailySummary } from "@heartsteps/daily-summaries/daily-summary.model";

import * as moment from 'moment';
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { Subscription } from "rxjs";
import { Router } from "@angular/router";
import { DailySummaryService } from "@heartsteps/daily-summaries/daily-summary.service";
import { DateFactory } from "@infrastructure/date.factory";
import { CachedActivityLogService } from "@heartsteps/activity-logs/cached-activity-log.service";

@Component({
    selector: 'activity-log-daily-summary',
    templateUrl: './daily-summary.component.html'
})
export class DailySummaryComponent {

    @Input('date') day: Date;
    private dailySummary: DailySummary;

    public activities: Array<ActivityLog>;

    public isToday: boolean;
    public formattedDate:string;
    public totalMinutes: number;
    public totalSteps: number;
    public totalMiles: number;

    constructor (
        private dailySummaryService: DailySummaryService,
        private cachedActivityLogService: CachedActivityLogService,
        private dateFactory: DateFactory,
        private router: Router
    ) {
        
    }

    @Input('date')
    set setDate(date: Date) {
        if(date) {
            this.day = date;
            this.isToday = this.dateFactory.isSameDay(date, new Date());
            this.update();
            this.cachedActivityLogService.get(date)
            .subscribe((logs) => {
                this.activities = logs;
            })
            // this.dailySummaryService.get(this.day)
            // .then((dailySummary) => {
            //     this.dailySummary = dailySummary;
            //     this.update();
            // });
        }
    }

    public openActivityLog(activityLog) {
        this.router.navigate([{
            outlets: {
                modal: ['activities', 'logs', activityLog.id]
            }
        }]);
    }

    public addActivityLog() {
        this.router.navigate([{
            outlets: {
                modal: ['activities','logs','create']
            }
        }], {
            queryParams: {
                date: this.dateFactory.formatDate(this.day)
            }
        });
    }

    private update() {
        this.formatDate();
        if(this.dailySummary) {
            this.totalMinutes = this.dailySummary.minutes;
            this.totalSteps = this.dailySummary.steps;
            this.totalMiles = this.dailySummary.miles;
        }
    }

    private formatDate() {
        const summaryMoment = moment(this.day);
        this.formattedDate = summaryMoment.format("dddd, M/D");
    }

}
