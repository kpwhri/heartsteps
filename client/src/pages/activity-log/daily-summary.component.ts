import { Component, Input, OnDestroy } from "@angular/core";
import { DailySummary } from "@heartsteps/daily-summaries/daily-summary.model";

import * as moment from 'moment';
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { CurrentActivityLogService } from "@heartsteps/current-week/current-activity-log.service";
import { Subscription } from "rxjs";
import { Router } from "@angular/router";
import { DailySummaryService } from "@heartsteps/daily-summaries/daily-summary.service";
import { DateFactory } from "@infrastructure/date.factory";

@Component({
    selector: 'activity-log-daily-summary',
    templateUrl: './daily-summary.component.html'
})
export class DailySummaryComponent implements OnDestroy {

    private day: Date;
    private dailySummary: DailySummary;

    private activityLogSubscription: Subscription;
    public activities: Array<ActivityLog>;

    public formattedDate:string;
    public totalMinutes: number;
    public totalSteps: number;
    public totalMiles: number;

    constructor (
        private dailySummaryService: DailySummaryService,
        private currentActivityLogService: CurrentActivityLogService,
        private dateFactory: DateFactory,
        private router: Router
    ) {
        this.activityLogSubscription = this.currentActivityLogService.activityLogs
        .subscribe((activityLogs) => {
            this.filterActivities(activityLogs);
        })
    }

    ngOnDestroy() {
        if(this.activityLogSubscription) {
            this.activityLogSubscription.unsubscribe();
        }
    }

    @Input('date')
    set setDate(date: Date) {
        if(date) {
            this.day = date;
            this.update();
            this.dailySummaryService.get(this.day)
            .then((dailySummary) => {
                this.dailySummary = dailySummary;
                this.update();
            });
        }
    }

    @Input('dailySummary')
    set setDailySummary(summary: DailySummary) {
        this.day = summary.date;
        this.dailySummary = summary;
        this.update();
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
            this.filterActivities(this.currentActivityLogService.activityLogs.value);
        }
    }

    private filterActivities(activityLogs:Array<ActivityLog>) {
        if (this.dailySummary && activityLogs) {
            this.activities = activityLogs.filter((activityLog) => {
                if(moment(this.dailySummary.date).isSame(activityLog.start, 'day')) {
                    return true;
                } else {
                    return false;
                }
            })
        } else {
            this.activities = undefined;
        }
    }

    private formatDate() {
        const summaryMoment = moment(this.day);
        if(summaryMoment.isSame(new Date(), 'day')) {
            this.formattedDate = 'Today, ' + summaryMoment.format('M/D');
        } else {
            this.formattedDate = summaryMoment.format("dddd, M/D");
        }
    }

}
