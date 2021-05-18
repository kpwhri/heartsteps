import { Component, Input } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { DailySummary } from '@heartsteps/daily-summaries/daily-summary.model';
import { Router } from '@angular/router';

@Component({
    selector: 'pages-daily-summary-list',
    templateUrl: './daily-summary-list.component.html',
    providers: [
        DateFactory
    ]
})
export class DailySummaryListComponent {

    @Input('summaries') summaries:Array<DailySummary>;

    constructor(
        private router: Router,
        private dateFactory: DateFactory
    ) {}

    goTo(date:Date) {
        this.router.navigate(['activities', this.dateFactory.formatDate(date)])
    }
}
