import { Component } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { DailySummaryService } from '@heartsteps/activity/daily-summary.service';
import { DailySummary } from '@heartsteps/activity/daily-summary.model';
import { Router } from '@angular/router';

@Component({
    selector: 'heartsteps-activity-summary-list',
    templateUrl: './activity-summary-list.component.html',
    providers: [
        DateFactory
    ]
})
export class ActivitySummaryListComponent {

    summaries:Array<DailySummary>;

    constructor(
        private dateFactory: DateFactory,
        dailySummaryService: DailySummaryService,
        private router: Router
    ) {
        const days:Array<Date> = [];
        const today:Date = new Date();
        this.dateFactory.getCurrentWeek().forEach((day) => {
            if(day < today) {
                days.push(day);
            }
        })
        dailySummaryService.getWeek(days[0], days[-1]).then((summaries) => {
            this.summaries = summaries;
        });
    }

    goTo(date:Date) {
        console.log(date);
        this.router.navigate(['activities', this.dateFactory.formatDate(date)])
    }
}
