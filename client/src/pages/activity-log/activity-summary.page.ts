import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DateFactory } from '@infrastructure/date.factory';
import { Location } from '@angular/common';
import { ActivityLogService } from '@heartsteps/activity-logs/activity-log.service';
import { ActivityLog } from '@heartsteps/activity-logs/activity-log.model';
import { DailySummary } from '@heartsteps/daily-summaries/daily-summary.model';

@Component({
    selector: 'activity-summary-page',
    templateUrl: './activity-summary.page.html',
    providers: [
        DateFactory
    ]
})
export class ActivitySummaryPage implements OnInit {

    public dailySummary: DailySummary;
    public logs:Array<ActivityLog>;

    constructor(
        private activatedRoute: ActivatedRoute,
        private router: Router,
        private dateFactory: DateFactory,
        private location: Location,
        private activityLogService: ActivityLogService
    ) {}

    ngOnInit() {
        this.logs = this.activatedRoute.snapshot.data['activityLogs'];
        this.dailySummary = this.activatedRoute.snapshot.data['dailySummary'];
    }

    openActivityLog(log:ActivityLog) {
        this.router.navigate(['activities', 'logs', log.id]);
    }

    back() {
        this.location.back();
    }

}
