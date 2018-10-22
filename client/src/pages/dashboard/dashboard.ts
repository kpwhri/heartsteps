import { Component, OnInit } from '@angular/core';
import { IonicPage } from 'ionic-angular';
import { HeartstepsServer } from '@infrastructure/heartsteps-server.service';
import { ActivityLogService } from '@heartsteps/activity/activity-log.service';

@IonicPage()
@Component({
    selector: 'page-dashboard',
    templateUrl: 'dashboard.html',
    providers: [ActivityLogService]
})
export class DashboardPage implements OnInit {

    private totalSteps: Number;
    private totalActiveMinutes: Number;

    constructor(
        private activityLogService: ActivityLogService
    ) {
        
    }

    ngOnInit() {
        this.activityLogService.getSummary()
        .then((data: any) => {
            this.totalSteps = data.totalSteps;
            this.totalActiveMinutes = data.totalActiveMinutes;
        })
    }
}
