import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DateFactory } from '@infrastructure/date.factory';
import { Location } from '@angular/common';
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
        private location: Location,
    ) {}

    ngOnInit() {
        this.logs = this.activatedRoute.snapshot.data['activityLogs'];
        this.dailySummary = this.activatedRoute.snapshot.data['dailySummary'];
    }

    openActivityLog(log:ActivityLog) {
        this.router.navigate([{outlets:{
            modal: ['activities', 'logs', log.id].join('/')
        }}]);
    }

    back() {
        this.location.back();
    }

}
