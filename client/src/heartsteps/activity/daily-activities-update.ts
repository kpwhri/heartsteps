import { Component, OnInit, OnDestroy } from "@angular/core";
import { DailySummaryService } from "./daily-summary.service";


@Component({
    selector: 'heartsteps-activity-daily-update',
    templateUrl: './daily-activities-update.html'
})
export class DailyActivitiesUpdateComponent implements OnInit {
    public loading:Boolean;

    constructor(
        private dailySummaryService: DailySummaryService
    ){}

    ngOnInit() {
        this.dailySummaryService.summaries.subscribe(()=>{
            this.loading = false;
            console.log("updated!");
        })
    }

    public refresh() {
        this.loading = true;
        this.dailySummaryService.getDate(new Date());
    }
}