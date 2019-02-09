import { Component, Input } from "@angular/core";
import { DailySummaryService } from "./daily-summary.service";

import * as moment from 'moment';
import { LoadingService } from "@infrastructure/loading.service";
import { DailySummary } from "./daily-summary.model";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";

@Component({
    selector: 'heartsteps-activity-daily-update',
    templateUrl: './daily-activities-update.html'
})
export class DailyActivitiesUpdateComponent {
    
    public loading: boolean = false;
    public updateTimeFormatted:string;
    private summary: DailySummary;

    constructor(
        private dailySummaryService: DailySummaryService,
        private alertDialog: AlertDialogController
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
        this.loading = true;
        this.dailySummaryService.update(this.summary.date)
        .then((summary) => {
            this.summary = summary;
            this.formatTime();
        })
        .catch(() => {
            this.alertDialog.show('Update failed');
        })
        .then(() => {
            this.loading = false;
        });
    }
}