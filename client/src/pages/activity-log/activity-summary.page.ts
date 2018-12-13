import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DateFactory } from '@infrastructure/date.factory';
import { Location } from '@angular/common';
import { ActivityLogService } from '@heartsteps/activity/activity-log.service';
import { ActivityLog } from '@heartsteps/activity/activity-log.model';

@Component({
    selector: 'activity-summary-page',
    templateUrl: './activity-summary.page.html',
    providers: [
        DateFactory
    ]
})
export class ActivitySummaryPage implements OnInit {

    date:Date;
    logs:Array<ActivityLog>;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private dateFactory: DateFactory,
        private location: Location,
        private activityLogService: ActivityLogService
    ) {}

    ngOnInit() {
        this.date = this.dateFactory.parseDate(
            this.route.snapshot.paramMap.get('date')
        );
        this.activityLogService.get(this.date)
        .then((logs) => {
            this.logs = logs;
        })
    }

    back() {
        this.location.back();
    }

}
