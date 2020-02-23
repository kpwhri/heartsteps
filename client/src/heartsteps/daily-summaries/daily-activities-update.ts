import { Component, Input } from "@angular/core";
import { DailySummaryService } from "./daily-summary.service";

import * as moment from 'moment';
import { DailySummary } from "./daily-summary.model";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";
import { LoadingService } from "@infrastructure/loading.service";

@Component({
    selector: 'heartsteps-activity-daily-update',
    templateUrl: './daily-activities-update.html'
})
export class DailyActivitiesUpdateComponent {
    
    public loading: boolean = false;
    public updateTimeFormatted:string;
    private summary: DailySummary;

    public date:Date;

    constructor(
        private dailySummaryService: DailySummaryService,
        private alertDialog: AlertDialogController,
        private loadingService: LoadingService
    ) {}

    @Input('summary')
    set setSummary(summary: DailySummary) {
        if(summary) {
            this.update(summary)
        }
    }

    @Input('date')
    set setDate(date: Date) {
        if (date) {
            this.date = date;
            this.loading = true;
            this.dailySummaryService.get(date)
            .then((summary) => {
                this.update(summary);
            })
            .catch(() => {
                console.log('Could not get daily summary');
            })
            .then(() => {
                this.loading = false;
            });
        }
    }

    private formatTime() {
        this.updateTimeFormatted = moment(this.summary.updated).fromNow();
    }

    private update(summary: DailySummary) {
        this.summary = summary;
        this.formatTime();
    }

    public refresh() {
        this.loadingService.show('Requesting data from Fitbit');
        this.dailySummaryService.updateFromFitbit(this.summary.date)
        .then((summary) => {
            this.update(summary);
            this.loadingService.dismiss();
        })
        .catch(() => {
            this.loadingService.dismiss();
            this.alertDialog.show('Update failed');
        });
    }
}