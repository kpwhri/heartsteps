import { Component, OnInit, Input } from "@angular/core";
import { ActivityLog } from "./activity-log.model";


@Component({
    'selector': 'heartsteps-activity-log',
    templateUrl: './activity-log.component.html',
    inputs: ['activityLog']
})
export class ActivityLogComponent implements OnInit {
    @Input() activityLog:ActivityLog;

    type:string;
    start:string;
    end:string;

    totalMinutes:number;

    constructor() {}

    ngOnInit() {
        if(this.activityLog.type) {
            this.type = this.activityLog.type;
        } else {
            this.type = 'Walk'
        }

        this.start = this.activityLog.formatStartTime();
        this.end = this.activityLog.formatEndTime();
        this.totalMinutes = this.activityLog.totalMinutes;

    }
}