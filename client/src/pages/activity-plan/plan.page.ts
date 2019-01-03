import { Component } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { CurrentWeekService } from '@heartsteps/weekly-survey/current-week.service';
import { Week } from '@heartsteps/weekly-survey/week.model';

@Component({
    selector: 'page-plan',
    templateUrl: 'plan.page.html',
    providers: [DateFactory]
})
export class PlanPage {

    private week:Week

    constructor(
        private currentWeekService: CurrentWeekService
    ) {
        this.currentWeekService.week.subscribe((week) => {
            this.week = week;
        });
    }
}
