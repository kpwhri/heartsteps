import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { Location } from "@angular/common";


@Component({
    templateUrl: './activity-log.page.html'
})
export class ActivityLogPage implements OnInit {

    public activityLog:ActivityLog;

    constructor(
        private activatedRoute: ActivatedRoute,
        private location: Location
    ) {}

    ngOnInit() {
        this.activityLog = this.activatedRoute.snapshot.data['activityLog'];
    }

    back() {
        this.location.back();
    }
}
