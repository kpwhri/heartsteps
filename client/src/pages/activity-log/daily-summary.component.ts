import { Component, Input, OnDestroy } from "@angular/core";
import { DailySummary } from "@heartsteps/daily-summaries/daily-summary.model";

import * as moment from 'moment';
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { CurrentActivityLogService } from "@heartsteps/current-week/current-activity-log.service";
import { Subscription } from "rxjs";
import { Router } from "@angular/router";

@Component({
    selector: 'activity-log-daily-summary',
    templateUrl: './daily-summary.component.html'
})
export class DailySummaryComponent implements OnDestroy {

    private dailySummary: DailySummary;

    private activityLogSubscription: Subscription;
    public activities: Array<ActivityLog>;

    public formattedDate:string;
    public totalMinutes: number;
    public totalSteps: number;
    public totalMiles: number;

    constructor (
        private currentActivityLogService: CurrentActivityLogService,
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

    @Input('dailySummary')
    set setDailySummary(summary) {
        this.dailySummary = summary;
        this.formatDate();
        this.totalMinutes = this.dailySummary.minutes;
        this.totalSteps = this.dailySummary.steps;
        this.totalMiles = this.dailySummary.miles;
        this.filterActivities(this.currentActivityLogService.activityLogs.value);
    }

    public openActivityLog(activityLog) {
        this.router.navigate([{
            outlets: {
                modal: ['activities', 'logs', activityLog.id]
            }
        }]);
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
        const summaryMoment = moment(this.dailySummary.date);
        if(summaryMoment.isSame(new Date(), 'day')) {
            this.formattedDate = 'Today ' + summaryMoment.format('MMM D')
        } else {
            this.formattedDate = summaryMoment.format('ddd MMM D')
        }
    }

}
