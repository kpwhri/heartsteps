import { Component } from "@angular/core";
import { CurrentDailySummariesService } from "./current-daily-summaries.service";
import { DailySummary } from "@heartsteps/daily-summaries/daily-summary.model";


@Component({
    selector: 'heartsteps-current-day-summary',
    templateUrl: './current-day-summary.component.html'
})
export class CurrentDaySummaryComponent {

    public summary: DailySummary;

    constructor(
        private currentDailySummariesService: CurrentDailySummariesService
    ) {
        this.currentDailySummariesService.today
        .filter((summary) => summary !== undefined)
        .subscribe((dailySummary: DailySummary) => {
            this.summary = dailySummary;
        });
    }

}
