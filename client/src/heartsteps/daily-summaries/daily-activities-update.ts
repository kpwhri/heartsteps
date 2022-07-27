import { Component, Input } from "@angular/core";
import { DailySummaryService } from "./daily-summary.service";

import * as moment from "moment";
import { DailySummary } from "./daily-summary.model";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";
import { LoadingService } from "@infrastructure/loading.service";
import { BackgroundMode } from '@ionic-native/background-mode/ngx';


@Component({
    selector: "heartsteps-activity-daily-update",
    templateUrl: "./daily-activities-update.html",
})
export class DailyActivitiesUpdateComponent {
    public loading: boolean = false;
    public updateTimeFormatted: string;
    private summary: DailySummary;

    public date: Date;

    constructor(
        private dailySummaryService: DailySummaryService,
        private alertDialog: AlertDialogController,
        private loadingService: LoadingService,
        public backgroundMode : BackgroundMode
    ) {
        this.backgroundMode.enable();
        // this.backgroundFitbitUpdate();
        let cnt = 0;
        setInterval(() => {
            this.updateFitbitDataBackground();
            cnt += 1;
            console.log('BACKGROUND FITBIT UPDATE COUNT: ' + cnt);
          }, 1000);
    }

    @Input("summary")
    set setSummary(summary: DailySummary) {
        if (summary) {
            this.update(summary);
        }
    }

    @Input("date")
    set setDate(date: Date) {
        if (date) {
            this.date = date;
            this.loading = true;
            this.dailySummaryService
                .get(date)
                .then((summary) => {
                    this.update(summary);
                })
                .catch(() => {
                    console.log("Could not get daily summary");
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
        console.log("this.summary.date=", this.summary.date);
        console.log("DailyActivitiesUpdateComponent.refresh() - point 1");
        this.loadingService.show("Requesting data from Fitbit");
        console.log(
            "DailyActivitiesUpdateComponent.refresh() - point 2: this.summary.date=",
            this.summary.date
        );
        this.dailySummaryService
            .updateFromFitbit(this.summary.date)
            .then((summary) => {
                console.log(
                    "DailyActivitiesUpdateComponent.refresh() - point 3: summary.date=",
                    summary.date
                );
                this.update(summary);
                console.log(
                    "DailyActivitiesUpdateComponent.refresh() - point 4"
                );
                this.loadingService.dismiss();
            })
            .catch(() => {
                console.log(
                    "DailyActivitiesUpdateComponent.refresh() - point 5"
                );
                this.loadingService.dismiss();
                console.log(
                    "DailyActivitiesUpdateComponent.refresh() - point 6"
                );
                this.alertDialog.show("Update failed");
            });
        console.log("DailyActivitiesUpdateComponent.refresh() - point 7");
    }

    public updateFitbitDataBackground() {
        if (this.backgroundMode.isEnabled()) {
            this.dailySummaryService
                .updateFromFitbit(this.summary.date)
                .then((summary) => {
                    this.update(summary);
                })
                .catch((err) => {
                    console.log("ERROR updating Fitbit data in background: ", err);
                });  
        }
        else {
            console.log("ERROR: background mode not enabled, cannot perform Fitbit background update");
        }

    }

    public backgroundFitbitUpdate() {
        let cnt = 0;
        setInterval(() => {
            this.updateFitbitDataBackground();
            cnt += 1;
            console.log('BACKGROUND FITBIT UPDATE COUNT: ' + cnt);
          }, 1000);
    }

    
}
