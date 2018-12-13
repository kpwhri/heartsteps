import { Component, OnInit } from "@angular/core";
import { DailySummaryService } from "./daily-summary.service";

import * as moment from 'moment';

@Component({
    selector: 'heartsteps-activity-daily-update',
    templateUrl: './daily-activities-update.html'
})
export class DailyActivitiesUpdateComponent implements OnInit {
    public loading:Boolean;
    public lastUpdate:Date;
    public updateTimeFormatted:string;

    constructor(
        private dailySummaryService: DailySummaryService
    ){}

    ngOnInit() {
        this.dailySummaryService.updateTime.subscribe((date:Date)=>{
            this.loading = false;
            if(date) {
                this.lastUpdate = date;
                this.formatTime();
            }
        });
    }

    private formatTime() {
        this.updateTimeFormatted = moment(this.lastUpdate).fromNow();
    }

    public refresh() {
        this.loading = true;
        this.dailySummaryService.getDate(new Date());
    }
}