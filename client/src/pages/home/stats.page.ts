import { Component, OnInit } from "@angular/core";
import { CurrentWeekService } from "@heartsteps/current-week/current-week.service";
import { DailySummaryService } from "@heartsteps/daily-summaries/daily-summary.service";
import { DailySummary } from "@heartsteps/daily-summaries/daily-summary.model";


@Component({
    templateUrl: './stats.page.html'
})
export class StatsPage implements OnInit {

    public dailySummaries: Array<DailySummary>;

    constructor(
        private currentWeekService: CurrentWeekService,
        private dailySummaryService: DailySummaryService
    ){}

    ngOnInit() {
        this.currentWeekService.get()
        .then((week) => {
            this.dailySummaryService.getWeek(week.start, week.end)
            .then((dailySummaries) => {
                this.dailySummaries = dailySummaries;
            });
        })
    }
    
}
