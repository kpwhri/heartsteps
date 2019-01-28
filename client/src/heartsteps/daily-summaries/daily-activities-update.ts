import { Component, OnInit } from "@angular/core";
import { DailySummaryService } from "./daily-summary.service";

import * as moment from 'moment';
import { LoadingService } from "@infrastructure/loading.service";

@Component({
    selector: 'heartsteps-activity-daily-update',
    templateUrl: './daily-activities-update.html'
})
export class DailyActivitiesUpdateComponent implements OnInit {
    public lastUpdate:Date;
    public updateTimeFormatted:string;

    constructor(
        private dailySummaryService: DailySummaryService,
        private loadingService: LoadingService
    ){}

    ngOnInit() {
        this.dailySummaryService.updateTime.subscribe((date:Date)=>{
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
        this.loadingService.show("Loading data from Fitbit");
        this.dailySummaryService.getDate(new Date())
        .catch(() => {

        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }
}