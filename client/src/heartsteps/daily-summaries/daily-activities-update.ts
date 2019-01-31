import { Component, OnInit, Input } from "@angular/core";
import { DailySummaryService } from "./daily-summary.service";

import * as moment from 'moment';
import { LoadingService } from "@infrastructure/loading.service";
import { DailySummary } from "./daily-summary.model";

@Component({
    selector: 'heartsteps-activity-daily-update',
    templateUrl: './daily-activities-update.html'
})
export class DailyActivitiesUpdateComponent {
    
    public updateTimeFormatted:string;
    private summary: DailySummary;

    constructor(
        private dailySummaryService: DailySummaryService,
        private loadingService: LoadingService
    ){}

    @Input('summary')
    set setSummary(summary: DailySummary) {
        if(summary) {
            this.summary = summary
            this.formatTime();
        }
    }

    private formatTime() {
        this.updateTimeFormatted = moment(this.summary.updated).fromNow();
    }

    public refresh() {
        if (this.summary) {
            this.loadingService.show("Loading data from Fitbit");
            this.dailySummaryService.update(this.summary.date)
            .then((summary) => {
                this.summary = summary;
                this.formatTime();
            })
            .catch(() => {
                console.log('Could not get summary');
            })
            .then(() => {
                this.loadingService.dismiss();
            });
        }
    }
}